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

| # | phase | destructive? | gate to the next phase |
|---|---|---|---|
| **0** | Proposal — architecture, conventions, schemas, taxonomies, L0 diagram | no | the proposal reads coherently and the design decisions are justified |
| **1** | Build the graph, the checker and the generated views; add the fail-red guards | no | `systems_check.py --check` green; all existing linters still green |
| **2** | Retire the patient-facing site; promote its clinical data | **yes** | the two research consumers of the clinical dataset still run |
| **3** | Decompose the program map into the hierarchy | **yes** | zero unresolved anchors across all referrers; the plan parser reports the same item count as before |
| **4** | Documentation consolidation, archive, rewrite the canonical set | **yes** | frontmatter complete; no concept claimed by two documents |
| **5** | Wire technology monitoring into the graph; populate forecasts and the multi-year roadmap | no | every non-permanent blocker maps to a technology; every technology has a dated forecast |
| **6** | *Optional, separately reviewed* — repository hygiene | **yes** | — |

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
| `METHODOLOGY.md` | Reframed from *"the most dangerous part of the site"* to the repository's evidence contract, which is what it always was — five of its six sections are what the manuscript's meta-analysis assumes and does not re-check. §2 now states plainly that **two pooling methods exist and are not interchangeable**. ⏳ Moves to `systems/POLICY-evidence.md` in Phase 4, where ~15 inbound references get repointed together. |
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

*(Phases 4–5 rows are appended as those phases land. A phase is not complete until its rows are here.)*

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
