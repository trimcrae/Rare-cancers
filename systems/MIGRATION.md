---
id: DOC-MIGRATION
title: Migration plan and forwarding-address register
level: L0
kind: policy
status: live
canonical_for: [migration phases, what replaced what, where superseded information now lives, open decisions]
purpose: >
  Record the plan for moving this repository to the systems architecture, and — permanently — where
  every superseded document's information went, so nothing is dropped without a forwarding address.
scope: >
  The whole migration. Section 3 is a living register that outlives the migration itself: it is how a
  reader who follows an old link finds the current home.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-05
last_verified: 2026-08-05
related: [DOC-ARCHITECTURE, DOC-CONVENTIONS, DOC-TAX-BLOCKERS, DOC-TAX-TECHNOLOGY]
---

# Migration plan and forwarding-address register

> **Role:** what is being changed, in what order, and where everything went.
> §3 is the part that matters after the migration ends — it is the redirect table.

---

## 1 · Principles

1. **Additive first.** The model is built, checked and generating views *before* any existing document is
   moved. If the migration stopped after Phase 1 the repository would be strictly better off and nothing
   would be broken.
2. **Repoint in the same commit as the move.** A parser, a pointer and the thing it points at travel
   together. Splitting them across commits is how a routed edit dies silently.
3. **Nothing is dropped without a forwarding address.** Every superseded document gets a row in §3 naming
   what replaced it and where its information now lives.
4. **Guards fail red before anything moves.** A parser that exits successfully when it cannot find what it
   parses is the most dangerous thing in the repository during a restructure — the plan would silently stop
   being read and every build would stay green.
5. **Reversible where practical.** Archive rather than delete when the content has provenance value; delete
   only where git history is genuinely the right record.

---

## 2 · Phases

| # | phase | state | destructive? |
|---|---|---|---|
| **0** | Proposal — architecture, conventions, schemas, taxonomies, L0 diagram | ✅ **done** | no |
| **1** | Build the graph, the checker, the generated views and the fail-red guards | ✅ **done** | no |
| **2** | Retire the patient-facing site; promote its clinical data | ✅ **done** | yes |
| **3** | Decompose the program map into the hierarchy | ✅ **done** — see §2.1 | yes |
| **4** | Documentation consolidation, archive, rewrite the canonical set | ◐ **partly done** — see §2.2 | yes |
| **5** | Technology register, forecasts, roadmap, maintenance, scan wiring | ✅ **done** — see §2.3 | no |
| **6** | *Optional, separately reviewed* — repository hygiene | ○ not started | yes |

### 2.1 · Phase 3 — what landed, and what deliberately did not

**Landed.** The requirement register is a first-class model object with a generated view, and the two
sections that restated it — the coverage matrix and the dependency graph — are now derived from it rather
than maintained by hand. The extraction is lossless and a check re-parses the roadmap on every run so the
two cannot diverge (§3.3).

**Also landed, 2026-08-05.** THE ORDERED PLAN and the money/ladder/spine block moved out of the roadmap
entirely — 1,584 lines — into [`graph/plan.json`](graph/plan.json) → [`views/plan.md`](views/plan.md).

⚠ **They had to move as ONE unit, and the reason is not obvious.** `pinned-figures.json`
`subset_checks/strategy_spine_cum` is a **within-file** check: it scans a single file for `Cum. ~$N`
(the plan) and `Cum ~$N` (the spine) and asserts the second is a subset of the first. The notations
differ deliberately. Splitting them across files fails as *"pattern found nothing"* — which reads like
a broken regex rather than a broken move. A third coupling was checked and was safe: three
realised-spend figures also require the map, and all three live in the scoreboard, which did not move.

**Still not landed:** the narrative sections (§7, §8, §9) are not split into per-route memos. The
registers were safe to lift because they are tabular; narrative is not, and splitting it badly would
lose argument rather than relocate it.

⚠ **Do not repeat the mistake this phase nearly made, twice.** The requirement extraction was first
written with a 1,200-character cap and would have truncated two claim-ceiling cells. The plan
extraction now refuses to write unless re-rendering reproduces the source byte for byte. **A lossy
migration is a regression. Measure the loss before moving anything, and prove it is zero.**

⭐ **And a regression the move itself caused:** `lint_claims` fell from 50 warnings to 43 the moment the
sections left, because ~1,580 lines of gate language walked out of the linted set and nothing said so.
A linter whose SCOPE shrinks while its PASS RATE improves is the worst possible signal. The generated
view is now a lint target and `parser_guard` asserts the coupling.

### 2.2 · Phase 4 — what landed, and the hazard that stopped the rest

**Landed.** `README.md`, `AGENTS.md`, `CONTRIBUTING.md` and the evidence contract (then `METHODOLOGY.md`,
now [`systems/POLICY-evidence.md`](./POLICY-evidence.md)) were rewritten in Phase 2 because they described
deleted files (§3.2). Frontmatter is present on every document in `systems/`.

**Not landed:** the archive sweep of the one-off session reports and the audit cluster.

⛔ **CORRECTION, 2026-08-05 — this section was written from a partial grep and two of its statements were
wrong.** *Superseded, retained:* *"the roadmap cites all four **by relative filename** … would replace four
stale documents with five broken references."* An exhaustive sweep over all 39 candidates, all file types,
whole repo, measured instead:

- The roadmap cites **two** of the four, not four — `map-merge-inventory.md` (×3) and
  `map-audit-strategy.md` (×1). **`map-audit-manuscript.md` (829 lines) and `map-merge-spec.md` (138
  lines) have zero referrers anywhere in the repository** and are safe to archive today.
- The cluster's real inbound count is **10**, not five.

⚠ **And the actual hazard is worse than the one this section described, because none of it is a Markdown
link.** Three references break at *runtime or in CI*:

1. `research/manuscripts/verify_map_edit_anchors.py` **opens** `map-merge-inventory.md` — the path comes
   from `three-row-audit-map-edits.json` entry `E10`, which also cites it **by row**
   (`"section": "map-merge-inventory row 4"`). Moving it raises `FileNotFoundError`.
2. `pinned-figures.json` `targets[9]` is `nr4a3-paralogue-dynamics-categorical-test-2026-07-25.md`.
   `lint_consistency.py` emits `S-target-missing` as an **ERROR** for a declared target it cannot find, so
   moving that file turns `tests.yml` and `preflight.sh` red.
3. `.github/workflows/gpu-ternary-fep-vast.yml:3130` `awk`-reads `ternary-lane-guard-audit-2026-07-25.md`
   to print an on-record baseline table. It falls through to a `||` branch rather than failing — which is
   worse than failing: the baseline silently disappears from the readout, which is the exact defect the
   surrounding comment exists to prevent.

**The measured tiers: 10 safe to archive today · 22 need repointing · 7 must never be archived** (a
preregistration freeze addendum, the `pinned-figures` target, the workflow-read audit, an `evidence_home`
of two *watching* scan triggers, a document cited by the flagship paper and a prereg's frozen-endpoint
caveat, the "rationale of record" reviewer verdict, and the red-team log — which `preprint-plan.md`
schedules for the **Supporting Information**, not the archive).

⭐ **Two date-stamped documents are not stale at all.** `three-row-audit-2026-08-03.md` and
`r3-site-choice-audit-2026-08-03.md` are two days old and are cited by `systems/graph/requirements.json`
itself. Their filenames made them look like one-off reports. That is why the frontmatter backfill precedes
the sweep: `kind` and `status` decide what is archivable, never the filename.

### 2.3 · Phase 5 — what landed

**Landed.** The technology register (24 dependencies), the forecast register (24 scenario-banded forecasts,
each declaring its basis), the multi-year roadmap generated as a projection of them, and
[`MAINTENANCE.md`](MAINTENANCE.md).

**Also landed, 2026-08-05.** The literature scan now writes into the graph — but **not** as originally
recommended. `MAINTENANCE.md` §5 had said a graded hit "should set `current_state`". ⛔ That would have
been wrong: the scan's own contract is that every hit is an unvalidated lead, machine-matched on a
title, and that nothing may change a status by itself. What was built instead is a `pending_signals[]`
queue on each `TECH-*` — the scan appends to it and touches nothing else, asserted by a test that should
never need relaxing. Grading stays a human read.

The interop check is now **bidirectional**, closing a gap `trigger_scan.py` documented against itself:
its docstring said the reverse direction "cannot be checked until the registry carries that field; as
of 2026-08-03 it does not." It did. The docstring was stale for two days and is corrected in place.

⭐ **Also recorded there rather than fixed:** one layer of the technology watch is credited in two documents
with auto-capturing advances and has never written an entry. Fixing or retiring it is a decision, not a
task, so it is surfaced rather than resolved.

### Phase 2 — the two things that will break if done carelessly

**(a) The Pages workflow and the site files must go in one commit.** The deploy workflow's `paths-ignore`
does not cover the site paths, so a commit that deletes the files while leaving the workflow triggers a build
that fails at the copy step — permanently red `main`, for a site nobody wants.

**(b) The clinical dataset has two research consumers that no text search will find.** Both build the path
segment by segment, so the directory name never appears as a literal string:

- `research/meta/meta-analysis.mjs` — the manuscript's random-effects meta-analysis engine. Reads the
  registry's citations and cohorts, writes results that a manuscript quotes. No fallback: it throws if the
  file moves.
- `research/hypotheses/enumerate-drugs.mjs` — uses the registry's treatment evidence as the **exclusion
  list** for repurposing gap analysis. Without it, drugs already tried in EMC would be reported as novel.

Both are patched in the same commit as the move, and both are run as the gate.

**(c) Two orphaned research tests.** The root `tests/` directory holds tests for the degradation model and
pose validity. They are research tests, not site tests, and **no CI job runs them** — every workflow's
`pytest tests/...` resolves to the modalities suite via a working directory. They move into that suite,
which also starts running them.

### Phase 3 — why this is the risky one, and what makes it survivable

161 files reference the program map and seven CI checks parse it by exact heading string. Renaming a heading
does not fail the build — it makes the check go **quiet**. The order below exists to make every failure loud
and early:

1. **Fail-red guards land first** (Phase 1). Every parser exits non-zero when it cannot find its anchor.
2. **The anchor-redirect map is published before any move**, and the checker fails on any unresolved anchor
   repo-wide — so a stale pointer is caught at the moment it goes stale, not months later.
3. **Registers move before narrative.** The registers are structured data and their generated form is
   verifiable against the original; narrative is not.
4. **Heading strings that CI parses are preserved verbatim in the generated views.** The ordered plan keeps
   its exact heading; the parser is repointed at the new file, not taught a new heading.
5. **The numeric contract is updated in the same commit as the ladder move.** A linter requires the ladder
   total to appear in three named files; moving one without updating the registry turns a correct document
   into a build failure.
6. **Structured referrers are repointed programmatically**, not by hand: the registry's `owner{file,anchor}`
   pointers, the scan triggers' evidence homes, and the anchor-based roadmap-edit subsystem.

The program map ends as a short generated index into the new views, so every inbound link still resolves.

**`STRATEGY.md` is not touched at all.** Its Appendix A rows are cited *as data* by dozens of files and its
heading is used as a structural clear by a linter. It is a database table wearing a document's clothes, and
the correct handling of one of those is to leave it alone.

---

## 3 · Forwarding-address register

> **This is the part that outlives the migration.** A reader following an old link, or an agent resolving a
> stale citation, finds the current home here.

Rows are added as each phase lands. `status` values: **moved** (content relocated intact) · **superseded**
(content replaced by something better) · **archived** (kept for provenance, no longer live) · **deleted**
(removed; git history is the record) · **split** (content divided between homes).

### 3.1 · Architecture and navigation

| was | status | now | note |
|---|---|---|---|
| `research/README.md` — structure section | superseded | [`ARCHITECTURE.md`](ARCHITECTURE.md) | described a structure with a patient-education rail that no longer exists |
| `AGENTS.md` — architecture section | superseded | [`ARCHITECTURE.md`](ARCHITECTURE.md) | described the static-site file map |
| `research/manuscripts/README.md` — index role | superseded | `views/L0-ecosystem.md` + `views/L1-*.md` | the index is now generated from the model, so it cannot go stale |
| `nr4a3-program-map.md` §0 — reading rules, glyphs, ID scheme, invariants | moved | [`CONVENTIONS.md`](CONVENTIONS.md) | ID collisions resolved in the move, see `CONVENTIONS.md` §1.1 |

### 3.2 · The patient-facing site (Phase 2, 2026-08-05)

**Deleted.** The interface and its tooling. Git history is the record; nothing referenced them.

| was | status | note |
|---|---|---|
| `index.html`, `404.html`, `cancers/emc/index.html` | deleted | page shells |
| `assets/css/styles.css`, `assets/js/cancer.js`, `assets/js/hub.js` | deleted | referenced only by the HTML |
| `templates/cancer-shell.html`, `templates/cancer.template.json` | deleted | read only by the scaffolding script |
| `data/index.json`, `data/schema.json` | deleted | site index and its field definitions |
| `scripts/new-cancer.mjs`, `scripts/smoke-render.mjs` | deleted | scaffolding and a DOM-shim renderer |
| `.claude/skills/add-cancer/` | deleted | every dependency of the skill was removed with it |
| `.github/workflows/pages.yml` | deleted | **in the same commit as the files above** — its `paths-ignore` does not cover the site paths, so deleting the files while keeping the workflow would have left `main` permanently red at the copy step |

**Promoted.** Never site tooling; the framing was what made them look like it.

| was | status | now | note |
|---|---|---|---|
| `data/cancers/emc.json` | moved | [`research/data/emc-clinical-registry.json`](../research/data/emc-clinical-registry.json) | The repository's only structured EMC clinical-evidence store. Registered as `ART-EMC-CLINICAL-REGISTRY`. Two consumers patched in the same commit — `research/meta/meta-analysis.mjs` and `research/hypotheses/enumerate-drugs.mjs` — **both of which build the path segment-by-segment, so a text search for the old directory name finds neither.** Verified: the meta-analysis output is byte-identical after the move. |
| `scripts/validate.mjs` | moved | `scripts/validate-registry.mjs` | Gate 2 of `preflight.sh`. Deleting it with the site would have made preflight report FAILED on every invocation forever. Site-presentation checks removed (index cross-reference, centre coordinates, live trial-search links); every evidence-contract check kept, because the meta-analysis assumes them and does not re-check them. |
| root `tests/test_degradation_model.py`, `tests/test_pose_validity.py` | moved | `research/modalities/tests/` | ⭐ Research tests that **no CI job ran**: every workflow's `pytest tests/…` resolved to the modalities suite via a working directory, so the root directory was never collected. Six tests that had never executed now run and pass. |

**Rewritten.** These described deleted files, so Phase 2 could not leave them.

| file | what changed |
|---|---|
| `README.md` | Rewritten around the L0 view as the entry point. |
| `AGENTS.md` | ~70 % was the site playbook — architecture file map, add-a-cancer procedure, editing rules, deployment. Removed. Medical integrity, literature ingestion, figures, tests and publishing kept and re-scoped to the research program. Two long-dead references removed: a branch that no longer exists and a CI file that never did. |
| `CONTRIBUTING.md` | Was ~100 % site. Rewritten as how to add a research object to the model. |
| `METHODOLOGY.md` → [`systems/POLICY-evidence.md`](./POLICY-evidence.md) | Reframed from *"the most dangerous part of the site"* to the repository's evidence contract, which is what it always was — five of its six sections are what the manuscript's meta-analysis assumes and does not re-check. §2 now states plainly that **two pooling methods exist and are not interchangeable**. ✅ **Moved 2026-08-05.** See §3.5 — the move was held back deliberately, and the reason it was worth holding back turned out not to be the one recorded here. |
| `CLAUDE.md` | Site block replaced with a pointer to `systems/`. The old *"the site is shelved — keep it working"* line is retained as superseded, because it is the instruction this phase reverses. |

### 3.3 · The requirement register (Phase 3, 2026-08-05)

| was | status | now | note |
|---|---|---|---|
| roadmap §2.1 — the requirement register table | **split** | machine home: [`systems/graph/requirements.json`](graph/requirements.json) · rendered to [`views/registers/requirements.md`](views/registers/requirements.md) | The roadmap keeps the ARGUMENT; the graph holds the STATE. Extraction is **lossless** — every claim-ceiling cell is stored verbatim, proven by a check that re-parses the roadmap on every run and fails if either side has been hand-edited away from the other. A capped extraction was written first and rejected: two ceilings would have been truncated, and a lossy migration is a regression, not a move. |
| roadmap §3.2 — the R×V coverage matrix | superseded | generated inside the same view | It is a pure function of the register above it, so it was a hand-maintained copy of a derivable fact. It is now derived and can no longer drift from the register it summarises. |
| roadmap §4 — the dependency graph | superseded | generated inside the same view | Node states are read from the requirement register rather than typed, so a requirement changing state can no longer leave the diagram stale. |

⭐ **What the extraction found.** The roadmap's prose says five requirements have no instrument at all.
Derived from the register itself, the count is also five — but **not the same five**: one row the prose
lists as a hole does have an instrument (the roadmap itself notes elsewhere that this row *"overstated
the gap"*), and one delegated row was not counted. The generated view therefore separates the two gaps
the prose merged: **no instrument exists** (5) versus **instruments exist but none has returned a usable
answer** (6). Those are opposite work items — the first needs something built or a bench, the second
needs a better method — and merging them is the same failure the technology taxonomy found on the watch
list, one layer down.

### 3.4 · Archived documents (§2, 2026-08-05)

Nine documents with **zero inbound references anywhere in the repository**, verified across every file
type rather than just Markdown links. Nothing needed repointing, which is why these went first.

| was | now | why it qualified |
|---|---|---|
| `research/manuscripts/map-audit-manuscript.md` | [`archive/manuscripts/`](../archive/manuscripts/map-audit-manuscript.md) | 829 lines pinned to a commit and a line count that have both moved. Zero referrers — contradicting what §2.2 originally claimed. |
| `research/manuscripts/map-merge-spec.md` | [`archive/manuscripts/`](../archive/manuscripts/map-merge-spec.md) | Carries its own `⛔ SUPERSEDED IN PART` banner. Zero referrers. |
| `research/manuscripts/nr4a3-degrader-paper-review-round3.md` | [`archive/manuscripts/`](../archive/manuscripts/nr4a3-degrader-paper-review-round3.md) | Superseded by later rounds; zero referrers. |
| `research/manuscripts/nr4a3-degrader-paper-review-round5.md` | [`archive/manuscripts/`](../archive/manuscripts/nr4a3-degrader-paper-review-round5.md) | Zero referrers. |
| `research/manuscripts/nr4a3-degrader-paper-review-round6.md` | [`archive/manuscripts/`](../archive/manuscripts/nr4a3-degrader-paper-review-round6.md) | 33 lines; zero referrers. ⚠ "round-6 reviewer" appears in three modules as a *concept*, never as this filename — those are not file references and do not break. |
| `research/ternary-session-handoff.md` | [`archive/research/`](../archive/research/ternary-session-handoff.md) | A one-shot session start-prompt; zero referrers. |
| `research/modalities/SESSION-HANDOFF-2026-06-28.md` | [`archive/modalities/`](../archive/modalities/SESSION-HANDOFF-2026-06-28.md) | A June state, long overtaken; zero referrers. |
| `research/modalities/nr4a3-repurpose-handoff.md` | [`archive/modalities/`](../archive/modalities/nr4a3-repurpose-handoff.md) | One-off paste-into-thread doc; zero referrers. |
| `research/modalities/nrv04-covalent-input-admissibility-2026-07-25.md` | [`archive/modalities/`](../archive/modalities/nrv04-covalent-input-admissibility-2026-07-25.md) | Zero referrers — the roadmap cites the *panel-recovery* document, not this one. |

⭐ **A tenth was on the safe list and was NOT archived.** `nr4a3-reach-rule-correction-2026-07-25.md`
has zero inbound references and a date-stamped filename, so it looked archivable by every structural
measure. Its own banner says *"Numbers marked ⏳ are filled from the CI artifacts when they land"* — and
it still carries **fifteen** ⏳ markers. Those runs never landed, so the document is **live, not stale**,
and archiving it would have buried an open work item. Checking cost one grep.

#### ✅ The sweep is CLOSED — and the answer is not the one that was predicted

*Superseded, retained:* ***"Still outstanding: 22 documents that need their references repointed in the
same commit as the move, and 7 that must never be archived."*** **That estimate was wrong, and the way it
was wrong is the point.**

It was built from **filename shape and inbound-link counts** — the only evidence available before the
documents declared anything about themselves. Once the frontmatter backfill landed, the documents could be
asked directly, and **20 of the 22 declare `live`**: 14 manuscripts, 3 runbooks, 2 memos and — the one that
should have stopped the estimate on its own — **a preregistration**, which may never be archived under any
circumstances. A date-stamped filename and a thin inbound-link count had made a live research record look
like a one-off report.

**Final count: 9 archived, 0 remaining.** Every candidate that survived triage did so for a stated reason:

| verdict | n | why |
|---|---|---|
| archived | 9 | zero inbound references of any kind, verified across every file type (§3.4 above) |
| live, held back | 1 | `nr4a3-reach-rule-correction-2026-07-25.md` — fifteen ⏳ markers for runs that never landed |
| live, **mislabelled by the backfill** | 3 | its regex read a **partial** supersession as a whole one — below |
| retired but **kept in place** | 2 | the two preprint redirect stubs; archiving a redirect destroys it |
| history, deliberately reachable | 1 | `STRATEGY.md` — a correction register has to be citable, now `history_only: true` |
| never archivable | 11 | every preregistration in the repository |

⛔ **THE MISLABEL WAS MINE, AND A REGEX CANNOT FIX IT.** `STATUS_SIGNALS` matched any supersession banner,
including one that supersedes only *part* of a document — and each of the three said so in the very line
that matched:

- *"**EXECUTION-PLAN** SUPERSEDED … The **thesis** below **stands unchanged**"* — 10 inbound references
  including a lint test and two modules
- *"**Both quotations** are SUPERSEDED … **Nothing** in this lane's result depends on either"* — and this
  one is **`pinned-figures.json targets[9]`**, so believing the label would eventually have archived a
  document `lint_consistency.py` is contractually required to find
- *"the checklist below is **retained only for the still-relevant** pre-posting items"* — cited by
  `CLAUDE.md` as the pre-post checklist

The fix is a **refusal**, not a better pattern: when a retirement marker sits next to a partial-supersession
qualifier, `classify()` leaves the status `live` and writes `_status_needs_review` for a human. Under-claiming
is recoverable; a wrong `historical` archives a live document. Two checks now make the class visible from
CI — **`[D8]`** (a `pinned-figures` target or a project-instruction reference may not declare itself retired)
and **`[D7]`** (a supersession must name its successor).

⚠ **`[D8]` would have caught two of the three, not all three.**
`nr4a3-degrader-strategy-ternary-first.md` is in neither register; it was caught by reading its ten inbound
references. That residue is stated rather than papered over: **the automated guard covers documents CI or the
instructions depend on, and nothing else.**

### 3.5 · The evidence contract (2026-08-05)

| was | now | inbound references |
|---|---|---|
| `METHODOLOGY.md` | [`systems/POLICY-evidence.md`](./POLICY-evidence.md) | **31 across 20 files — of which only 15 were repointed.** |

⛔ **THE HAZARD WAS NOT THE ONE §3.3 PREDICTED.** That row said the move had to be atomic because
*"repointing some and not others would leave two homes for one contract."* True, and beside the point:
the actual hazard was that **two files were named `METHODOLOGY.md`**, and the other one —
[`research/hypotheses/METHODOLOGY.md`](../research/hypotheses/METHODOLOGY.md), a completely different
contract governing drug-repurposing hypotheses — is referenced *by the same bare string*. A
find-and-replace across those 31 sites would have silently redirected sixteen references about candidate
generation, the triage score and the treatment-advice firewall to a document about Wilson intervals.

The split is not visible from the string and had to be read one site at a time:

- **Repointed (15)** — anything about citation structure, pooling, double-counting or vintage:
  `CLAUDE.md` · `AGENTS.md` ×3 · `CONTRIBUTING.md` ×3 · `research/PROTOCOL.md` ×2 · `research/README.md`
  (the *no-fabrication* rule) · `hla_coverage.py` ×2 · `nr4a_paralogue_dynamics.py` ·
  `paralogue_pocket_contrast.py` · `hla-coverage-emc.md` · `novel-modalities-factcheck.md` ·
  `triage-literature.mjs` · `hla-coverage.json` · `emc-clinical-registry.json` ·
  `systems/graph/artifacts.json`.
- **Left alone (16)** — anything about §7, §7.4, the firewall, cataloguing or the triage score:
  `research/README.md` ×2 · `IDEAS.md` ×2 · `enumerate-drugs.mjs` ×3 · `enumerate-drugs.yml` ·
  `txgnn-emc-findings.md` ×2 · `repurposing-hypotheses.md` ×4 · `target-drug-matrix.json` ·
  `validate-research.mjs` · `fact-check-log.md` · `repurposing-hypotheses-review.md`.

⭐ **One line read as a self-reference and was not.** `research/hypotheses/METHODOLOGY.md` §4 opened
*"Inherits `METHODOLOGY.md` §1"* — sitting inside a file of that name, under a heading about citation
rules, describing the `sourceId` → `citations` structure, which is the **root** file's §1. Its own §1 is
candidate generation. It now names the other document explicitly, so a real cross-file inheritance is
visible instead of looking like a typo.

**No runtime coupling existed** — verified before moving: the path appears in no `pinned-figures.json`
target, no `parser_guard` registration and no workflow `awk`/`open`. The two data-string hits are prose
inside JSON; `validate-registry.mjs` checks `dataStatusBanner` for **presence**, not content.

### 3.6 · Artifacts recovered from `modalities-cache` (2026-08-05)

Started as *"one of the three baselined broken links"* and was not one.

The baseline entry for `emc-line-data-probe.json` guessed *"either the probe was never run, or its output
was never committed."* **Both guesses were wrong.** `emc_line_data_probe.py` had run and had committed — to
**`modalities-cache`**, the branch `fusion-cpu-extras.yml` writes to. The artifact existed the whole time,
one ref away, while a manuscript here cited it as though it sat beside it.

⚠ **And it was 41 files, not one.** Of those, **24 were cited from this branch.** The repo-wide
relative-link checker had caught **one** of the 24 — correctly, and that is the finding: it validates the
*shape* of a Markdown link, and this repository cites results as bare backticked filenames in prose,
docstrings and JSON notes. **A checker that measures the shape of a citation cannot tell you whether the
thing cited exists.**

| action | n | reasoning |
|---|---|---|
| **ported** | 23 | cited from here; every one parses and none carries unflagged synthetic data |
| **left on the cache branch** | 1 | `vast-board-volatility.jsonl` — a live append-only price log (3.9 MB, one sample per run) whose only referrer is its own producer's `--out` default. Porting a snapshot would create a second, immediately-stale home |
| **left alone** | 17 | uncited from here, so they break nothing |

**The durable fix is `[K1]`**, not the port: it flags any artifact cited by name whose **producer exists in
this repo** but whose output is absent here — scoped that way so a forward reference to something nobody has
built reads as a plan rather than as drift. It found three more immediately;
each was checked against every branch and is genuinely unproduced, which is the other legitimate answer.
⚠ *Superseded, retained: the example given here was `nr4a3-5bt-signature.json`, and it was the WRONG example —
that artifact was not a forward reference at all but a silent failure of a step that had already run (§3.9).
It was produced on 2026-08-05 and is committed here; the scoping argument stands, the illustration does not.*

⛔ **Port-then-switch, and only the port was done.** No workflow's target branch was changed. Repointing a
lane is the expensive half — `CLAUDE.md` §7 records a case where flipping one would have shown 13 finished
edges as unrun and re-bought them — and it is not this migration's to make.

### 3.7 · Repository hygiene — 383 MB of telemetry that was never evidence (2026-08-05)

`results/` was **551 MB of committed simulation output**, and the first reading of that number was the wrong
one: *"this is scientific evidence behind manuscript claims, and deleting it trades a reversible
inconvenience for an irreversible loss."* That reasoning is correct — and it was being applied to the wrong
files.

**Measured before touching anything.** 70 % of `results/` — **383 MB, 1467 of 2082 files, across 4 job
directories** — was `profiler-output/system/incremental/**`: SageMaker Debugger's default system-metrics
dump, one JSON line per sample:

```
{"Type":"gpu","Name":"gpu0","Dimension":"GPUUtilization","Value":71.00, …}
{"Type":"i/o","Name":"IOPS","Dimension":"","Value":53507.20, …}
```

Every one of the 1467 files matched `system/incremental/N/N.algo-1.json`. **Nothing in the repository read a
byte of it** — no module, no workflow, no manuscript, no test. It is monitoring output, not measurement.

⭐ **The evidence and the bulk were inversely correlated, which is why the size was so misleading.** The
metadynamics record those directories sat beside — `HILLS`, `COLVAR`, `fes.dat`, the checkpoints and the
manifests — is a few MB and is untouched. The single most-cited subtree in `results/` is **1.2 MB with 44
referrers**; the three largest were 396 MB with 17 between them, and almost all of that was the telemetry.

| | before | after |
|---|---:|---:|
| `results/` | 551 MB · 2082 files | **168 MB · 615 files** |

⚠ **It returns on every new SageMaker job unless ignored** — which is exactly how it accumulated without
anyone deciding to keep it. `.gitignore` now carries `**/profiler-output/` with the measurement next to it,
so the next job cannot re-commit it silently.

### 3.8 · `systems/graph/link-baseline.json` — DELETED at zero, and both entries it ever explained were wrong (2026-08-05)

| was | is now |
|---|---|
| `systems/graph/link-baseline.json` | **deleted.** A broken relative link is an error. An artifact's absence is answered by a lane's `produces[]` or by [`artifact-refs.json`](graph/artifact-refs.json) |

The file opened at **120 known-broken relative links** and closed at none. That was its stated purpose —
*"This list is meant to reach zero. It must never grow."* — and `systems/tests/test_systems_check.py`
carried the instruction for what to do when it got there: *"an empty baseline should be deleted, not kept."*

⛔ **Keeping it empty would have been strictly worse than deleting it.** Nothing left to exempt, a standing
invitation to add a line instead of fixing a link, and — the real hazard — its loader guarded on
`os.path.exists`, so deleting the file by accident would have switched every exemption to "passes" without
saying a word. That is the fail-open shape `parser_guard` exists to catch.

⭐ **The two entries it ever held are the reason to be glad it is gone. Each carried a confident FREE-PROSE
reason that nothing could check, and each was wrong.**

1. The first blamed a probe that *"was never run, or its output was never committed."* Both guesses were
   wrong: `emc_line_data_probe.py` had run **and** committed — to `modalities-cache`, one ref away
   (§3.6). Measuring that divergence found 41 artifacts there, 24 of them cited from this branch.
2. The last said rung 5b-T *"is registered as NOT STARTED, so the artifact not existing is consistent."*
   ⛔ **Rung 5b-T ran on 2026-08-03 — twice**, and the gate this repository holds came from the SECOND
   run, at **9:19 AM ET**; that run committed `nr4a3-5bt-gate.json`, `nr4a3-5bt-frame.json` and both
   harness controls. ⚠ *Superseded, retained: "ran at 8:29 AM ET, and the same run committed …". Both
   runs are real; ours is byte-identical to the 9:19 commit and differs from the 8:29 one (NR4A1 arm 15
   vs 16 models, `p_focus_at_least` 0.10506 vs 0.59819), `NO-GO` in both.* `nr4a3-5bt-signature.json` was missing because its
   step was **the only line in `rung-5bt-ternary-rebuild.yml` written `|| true`** — it produced nothing,
   said nothing, and the following `git add` skipped a file that was never there. So the roadmap went on
   citing *"the `V1` read over all 16 models per arm"* for a read that existed on no ref, and the gate
   artifact carries no signature key either.
   ⭐ **ROOT-CAUSED AND CLOSED 2026-08-05, and the cause was not the `|| true` — that only hid it.** The step
   copied DeepTernary's `complex_pred_*.pdb` outputs to `*.cif` NAMES purely to satisfy
   `nr4a_ternary_signature`'s `*.cif`-only glob. `selcal_cofold_validate.parse_structure` dispatches on
   EXTENSION, so the rename routed PDB text into `parse_mmcif`, which raised `no _atom_site loop` on **every**
   run since the rung existed. Renaming a file to make a glob match is what broke it. Fixed at both ends —
   the glob accepts `*.pdb`, the staging keeps the real extension — and pinned by
   `test_the_v1_signature_glob_accepts_pdb_and_the_workflow_stages_it_as_pdb`.
   A new `signature_only_from_run` mode recomputed the read at **$0** from run `30816072204`'s own uploaded
   predictions (the 9:19 AM ET run this repo's gate came from, so both read one prediction set), and the
   artifact is committed. ⛔ **It deepens the `NO-GO` rather than softening it: zero sequence-encoded
   discriminating contacts in zero of the 16 NR4A3 models.** **Four fixes, all landed:** the `|| true` is
   gone and a failed read now writes a `_produced: false` artifact rather than nothing; the glob/extension
   mismatch is repaired; the roadmap's row carries the measured result with its superseded wording retained;
   and the `expected` disposition in [`artifact-refs.json`](graph/artifact-refs.json) is **removed**, because
   a disposition for a present artifact is a silencer.

⚠ **This is the same lesson as §3.5's, one register further out:** a `why` field with no rules is a place
for a plausible story to sit unchallenged. The registers that replaced it demand a *typed* disposition and
the evidence that disposition requires.

### 3.9 · The `verify` relation — where all 35 values of `instrument.serves` went (2026-08-05)

| was | is now |
|---|---|
| `requirement.served_by` | **`requirement.verified_by`** — SysML `verify`, the one asserted direction |
| `instrument.serves` | **deleted.** Every value re-homed; the table below is the forwarding address |
| `instrument.serves_derived` | **`instrument.verifies`** — derived, and now actually rendered |

⛔ **Three fields carried one relation, and the third was read by nothing.** Both `served_by` and `serves`
were asserted — the same edge written from both ends — so they could drift, and they had: **11 of 30
instruments disagreed with the requirement register**, six of them holding free prose in a field the rest
used for identifiers. `serves_derived` computed a fourth copy that no renderer, check or test consumed.

| the 35 values | where each went |
|---:|---|
| **19** | agreed with the requirement register already → pure duplicate, deleted |
| **4** | requirement ids the register lacked (`V19`→R7+R15, `V22`→R5, `INS-FUSION-COFOLD`→R13, `INS-MONOVALENT-REACH`→R8) → **added to `verified_by`** after reading each |
| **6** | paraphrases of an edge `route.instruments` **already carried** → deleted; the typed edge is the home, and it keeps the support-vs-disclosed-failing distinction the prose lost for five of the six |
| **6** | object-level definitions → **`instrument.characterises`** (SysML `refine`) |
| **2** | ⚖ **REFUSED, with the refusal recorded** — see below |
| **6** | genuine scope statements → **`instrument.scope_note`**, explicitly not a relation |

⚖ **Two claims were refused rather than merged, because merging them would have made the model say
something false.** `V3` claimed R8: it verifies R5, and R8's ceiling already declares itself *"conditional
on R5"* — a transitive reach is not a verification. `INS-FUSION-OBJECT-INVENTORY` claimed R13: its control
**passes**, and its own note says that pass is *"a statement about arithmetic, not about which junction is
reported"*, which is precisely what R13 asks — so it `characterises` `OBJ-MODEL-E7E3` and verifies nothing.
⚠ Adding it would have cleared R13's warning with an instrument that never addressed the question.

**Both source registers gained the schema they never had.** `instruments` and `requirements` were the only
two collections with none, which is how prose entered a relation field in the first place. `verified_by`,
`verifies` and `characterises` are now pattern-matched arrays, and `known_answer_control.state` is a closed
enum — including `mixed`, which was in use on two instruments, enumerated nowhere, and silently counting as
a pass.

**Warnings moved in both directions, which is the point.** `[W4]`×3, `[K0]` and `[K1]` closed; R4 and R16's
`[Q3]`s became stated scope boundaries; **R1 gained a `[Q4]`** because `mixed` stopped counting as a pass,
and R13's `[Q3]` became a `[Q4]` because it turned out to have an instrument after all. 16 → 10.

### 3.10 · Merging `main` back in — what nine hours of drift actually cost (2026-08-05)

CLAUDE.md §7 calls branch drift *"a data-loss bug, not an inconvenience"*, and this merge is the receipt.
`main` had moved **945 commits** since this branch's base — mostly CI artifact commits — and **21 files
overlapped**, including `nr4a3-program-map.md` and `emc-systems-map.json`, the two files this branch was
actively rewriting. Four conflicts, and **none of them was a formatting collision**:

| conflict | what it really was |
|---|---|
| `emc-surface-target-landscape.md` | this branch added the required frontmatter; `main` revised the H1. **Both wanted** — frontmatter kept, `main`'s title taken |
| `emc-systems-map.md` | a **generated** view. Regenerated, never hand-resolved |
| `method-watch-triggers.json` | both sides **appended** a trigger and git interleaved them. Merged by id: 29 from `main` + 4 from here. Verified against the merge base that this branch had edited **none** of the four common entries `main` changed |
| `tests/test_trigger_board_filter.py` | ⛔ **git's "helpful" relocation broke it.** `main` added it at repo-root `tests/`, which this branch deleted in Phase 2. Git moved it to `research/modalities/tests/`, where its two-level climb to the repo root resolved to `research/` — so it looked for `research/scripts/trigger_scan.py` and **errored at collection**. Fixed to four levels; the directory is right, because that is where CI actually runs it |

⭐ **And two real defects surfaced that neither side would have caught alone.**

1. **`INS-GEO-SERIES-CHARACTERISE` existed only in the legacy registry**, and `[L2]` said so. Porting it
   found its `serves` holding **two prose values** — the **seventh** instance of the untyped-relation
   defect (§3.9), *arriving on `main` while the other six were being removed here*. That is the strongest
   available argument for the typed relation: the field was still accreting paraphrases as it was being
   retired. Both values placed — one to `characterises`, one to `scope_note`. `OBJ-LINE-HEMCSS` — status `identity_disputed`, cited throughout ONLY as the cautionary
   precedent that an EMC label is not an EMC fusion — was ported with it as a **projection**: the eight fields the graph's object shape carries, with the
   `identity` verdict, `may_not_ground`, the 30-entry `read_by` sweep and its `_sweep_limit` left in the
   legacy registry, because the O3/O4 guards that enforce them live there and a second copy would be a
   second home for the fact those guards protect.
2. **`TRG-SARCOMA-ATRI-RESPONSE-PANEL` fired into nothing.** `main` added the trigger; no `TECH-*`
   watched it, so `[X3]` — the monitoring loop closed earlier in this migration — caught a scanner with
   no recorded consequence on its first exposure to work it did not come from. Wired to
   `TECH-EMC-EXPRESSION-DATA`: the trigger's own text says the expression ask is *"three-quarters
   satisfied"* while the response ask is *"wholly unsatisfied"*, which is two questions about one missing
   dataset family, sharing `BLK-NO-EMC-DATA`.

⚠ **A code collision was introduced here and is recorded so the next one is expected.** This branch's new
lane guard was written as `[X3]`, which `check_scan_interop` already owned — two checks under one code,
which would have made a warning unreadable in exactly the way §1 forbids. Renamed to `[X6]`.

*(A phase is not complete until its rows are here.)*

---

## 4 · Renames carried out during migration

Both resolve collisions that were documented as live hazards. Old spellings remain searchable as aliases.

| old | new | why |
|---|---|---|
| `C01`…`C16` (zero-padded instrument-options candidates) | `IC-1`…`IC-16` | collided outright with configuration items `C10`–`C16`; zero-padding was the intended tell and it ran out at ten |
| `C397`, `C420`, `C551`, … (residues) | `Cys397`, `Cys420`, `Cys551`, … | collided with the configuration register on every residue below 25 |
| "validation requirement 1–5" | `VR1`…`VR5` | one of five things called `R` |
| "lint rule R1–R5" | `LR1`…`LR5` | ditto |
| "Arm R1 / Arm R2" | `ARM-1` / `ARM-2` | ditto |
| the cycle-closure statistic `R` | `R_closure` | ditto |

---

## 5 · Open decisions

Surfaced rather than decided. Each names a recommendation and what would settle it.

### 5.1 · `CLAUDE.md` §6 — infrastructure reference inside a rules file

Roughly half of the agent instruction file is GPU/provider reference rather than standing rules, in a file
whose own opening says it stays short by construction and that anything restating other homes is a bug.

- **For moving it:** it would make the file honest to its own rule, and the reference material has natural
  homes in `research/compute/`.
- **Against:** it is load-bearing *because* it loads into every session. Every rule in it exists because it
  was violated, several of them expensively. Moving reference out of an always-loaded file and into one an
  agent must choose to open is a behaviour change with a real failure mode and no forcing deadline.

**Recommendation: leave it. Revisit after Phase 5**, when the runbook structure exists and the move would be
into somewhere already proven rather than somewhere new.

### 5.2 · The earlier repurposing / knowledge-graph layer

`research/hypotheses/` and its workflows are an earlier program layer: a drug-repurposing enumeration, a
target–drug matrix, and a pretrained knowledge-graph model's zero-shot ranking for EMC. It has no schedule,
no trigger, and no consumer inside the degrader program. But it is real work with real committed outputs, and
one of its findings — that the model diverges from mechanism-based enumeration — is a genuine limitation
result.

**Recommendation: register it live** as part of `ST-REPURPOSING`, with an honest `status` and a `maturity` of
`computed`, rather than archiving it. Drug repurposing is a first-class strategy family in this architecture,
and a family whose only computational asset is filed under history is a family that cannot be reasoned about.
Its dormancy then shows up where it belongs — in the route's `state` and `timing` — instead of being implied
by its location.

### 5.3 · How long the compatibility shim lives

`emc-systems-map.json` has eleven current consumers, including the weekly scan-trigger interop. During
Phase 1 it becomes a generated projection of the new graph so nothing breaks. It should not live forever — a
generated file that consumers treat as a source will eventually be written to.

**Recommendation:** retire it at the end of Phase 5, once the scan integration is repointed, and record the
retirement as a row in §3.

### 5.4 · Repository hygiene (Phase 6)

The results tree is large and fully git-tracked, and a substantial majority of its bytes are profiler
telemetry emitted by the training platform rather than scientific output. It passed the archiver's size cap
because of its file type, not because anything wanted it. Nothing in the repository cites it.

**Recommendation:** propose it as its own commit with its own review. It is unrelated to the architecture,
its risk profile is different — deleting committed data — and folding it into a documentation migration would
make both harder to review.
