---
id: DOC-CLAUDE
title: CLAUDE.md
level: —
kind: convention
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `convention` from its location under ./.
audience: [maintainers, autonomous research agents]
date: 2026-08-15
last_verified: 2026-09-04
_backfilled: true
---

# Standing research rules

Read [AGENTS.md](AGENTS.md) and the active
[operating protocol](research/autonomy/OPERATING_PROTOCOL.md). They apply to Claude and Codex.
The user's current instructions supersede historical process rules. Prior versions remain in Git
and [CLAUDE-history.md](CLAUDE-history.md); do not load the history unless diagnosing that incident.

## 0 · What to work on

PUB-ASO is the first manuscript to finish. Use its current package and existing reviews.
The degrader [roadmap](research/manuscripts/nr4a3-program-map.md) is a scientific reference for
that program, not mandatory startup context for unrelated work. Optimize for useful evidence
and patient outcomes. Keep one paper owner and one independent process change active.

## 1 · Writing and reporting

Keep derived values tied to their source. Correct current prose directly; preserve preregistrations
and record changes to pinned quantities in `research/manuscripts/pinned-figures.json`.
Do not embed retired instructions beside current ones. Keep replies concise and plain; manuscript
language retains scientific precision. Date status measurements and report unknowns honestly.

## 2 · Autonomy

Complete authorized, bounded work and report artifacts. Do not expand one task into every optional
backlog item. Continue independent work while tools run and keep the main conversation responsive.
Use tracked execution, finite tasks, and durable outcomes. Do not orphan work at turn end.
For owned parallel Claude Code work use `run_in_background`; shell `&` detaches work and is
blocked by the retained hook.

## 3 · Publication and spending authority

`research/autonomy/publication-authority.json` owns the grants; `publish_bar.py` and
`scripts/zenodo_deposit.py` enforce their respective paths. aiXiv has a standing scoped grant;
PUB-ASO is excluded. The Zenodo grant covers existing drafts subject to its recorded conditions.
Routine EMC research correspondence has a standing user grant in research_correspondence;
follow [the correspondence procedure](research/autonomy/correspondence/README.md) without per-message approval.
Journal submission and external acts outside the named grants require applicable user authorization.
Prepare the concrete package before seeking an approval that is actually needed.
The active budget posture in `research/autonomy/autonomy-state.json` takes precedence over old
generic spending thresholds. No paid API fallback and no GPU spending without applicable authority.

## 4 · Evidence

Never invent patient data, citations, measurements, or completion records. Retrieve sources and
distinguish measured results from projections. A successful launch is not delivery; a missing
measurement is unknown, not zero. Attribute every scientific finding to checkable evidence.

## 5 · Scope

There is no wet lab. Computational predictions cannot establish EMC efficacy, safety, selectivity,
or clinical readiness. Separate scientific blockers from optional tooling maintenance. Follow the
finite review procedure in the operating protocol; do not repeatedly rewrite a correct paper.

## 6 · Verification

Run checks appropriate to the change, batch fixes, and validate a settled tree once. Run the normal
`scripts/preflight.sh` commit gate; reserve `PREFLIGHT_FULL=1` for the publication candidate.
Preserve actual exit codes and test scope. A skipped test is not a pass. Never change a guard just
to hide an error. Administrative process changes are allowed by the current user instruction and
must describe the tradeoff in `research/autonomy/amendments.jsonl`.

## 7 · Repository and concurrency

Each writer gets an isolated worktree. One coordinator integrates work and updates shared state.
Remote legacy claims require `claim.py` and a successful push; local locks cannot coordinate
another machine. Do not run the legacy and replacement schedulers on the same work. Merge coherent
changes after checking current main, not after every edit. Preserve unmerged work and its evidence.
`systems/graph/*.json` owns model state; `systems/views/` is generated. The patient-facing site is
retired. Do not recreate it. Read `systems/POLICY-evidence.md` before editing the clinical registry.
