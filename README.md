---
id: DOC-README
title: EMC treatment-advancement research platform
kind: index
status: live
canonical_for: []
purpose: Repository entry point — what this is, and where to go first.
scope: Orientation only. It owns no fact; it points at the owner of each.
audience: [maintainers, autonomous research agents, external reviewers, collaborators]
date: 2026-08-05
last_verified: 2026-08-05
---

# EMC treatment-advancement research platform

> **What this is.** A computation-only research program working toward a treatment for **extraskeletal
> myxoid chondrosarcoma (EMC)**, an ultra-rare sarcoma driven by the EWSR1::NR4A3 fusion. One researcher,
> no wet lab, no funding for one — so every advance is either in-silico or publish-to-convince.
>
> **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness** for any route or
> molecule. Everything clinical is cited and never fabricated.

## Start here

| you want | read |
|---|---|
| **The whole landscape, in one screen** | 🗺️ **[`systems/views/L0-ecosystem.md`](./systems/views/L0-ecosystem.md)** — 9 strategy families, 40 routes, what holds each down, and the highest-leverage things to wait for |
| Why the repository is shaped this way | [`systems/ARCHITECTURE.md`](./systems/ARCHITECTURE.md) |
| What an identifier, glyph or status means | [`systems/CONVENTIONS.md`](./systems/CONVENTIONS.md) |
| Why work is stalled, and what would unstall it | [blocker taxonomy](./systems/taxonomy/blockers.md) · [technology taxonomy](./systems/taxonomy/technology.md) |
| The degrader program — the #1 deliverable | [`research/manuscripts/nr4a3-program-map.md`](./research/manuscripts/nr4a3-program-map.md): requirements, instruments, gates, the ordered plan, the spend ladder |
| The broader route portfolio as a decision record | [`research/manuscripts/emc-treatment-strategy.md`](./research/manuscripts/emc-treatment-strategy.md) |
| Standing rules for agents working here | [`CLAUDE.md`](./CLAUDE.md) |
| Where a superseded document went | [`systems/MIGRATION.md`](./systems/MIGRATION.md) |

⛔ **`STRATEGY.md` is history only** — two appendices whose rows are cited *as data* by dozens of files.
The roadmap wins on everything; that file wins only on what a superseded value used to be.

## How the repository is laid out

```
systems/     THE MODEL     graph/*.json is the source of truth; views/** are GENERATED and a
                           hand-edit fails the build. Answers "what is true, what is blocked,
                           what is next, and what would unblock it".
research/    THE WORK      manuscripts, preregistrations, memos, in-silico pipelines, artifacts,
                           compute infrastructure, and the cited EMC clinical registry.
scripts/     TOOLING       preflight (the pre-commit gate), the registry evidence contract,
                           literature ingestion, the named-capability literature scan.
results/     RAW OUTPUT    committed simulation output, with a durability ledger.
```

The boundary is the architecture's main invariant: **the model holds STATE, the work holds REASONING, and
every number has exactly one home.** Anything else that shows it is generated from that home.

## Working here

```bash
./scripts/preflight.sh                            # the pre-commit gate; its exit code cannot be masked
python3 systems/systems_check.py --check          # model invariants, pointer resolution, view drift
python3 systems/systems_check.py --write-views    # regenerate systems/views/** after a graph change
python3 systems/parser_guard.py                   # every registered parser can still find its input
```

The model layer has no dependencies and no build step — pure stdlib Python and plain JSON. Keep it that way.

## Retired

The repository formerly contained a patient-facing static site (GitHub Pages, one page per rare cancer).
**It is retired and deleted** — HTML, assets, templates, scaffolding scripts, the `add-cancer` skill and the
deploy workflow. Two things survived because they were never site tooling: the cited EMC clinical registry
([`research/data/emc-clinical-registry.json`](./research/data/emc-clinical-registry.json)), which the
manuscript meta-analysis and the repurposing gap analysis both read, and its evidence-contract validator
(`scripts/validate-registry.mjs`), which is gate 2 of preflight. Full accounting:
[`systems/MIGRATION.md`](./systems/MIGRATION.md).

> **Not medical advice.** Any clinical content here is educational information drawn from published
> literature and cannot replace an oncology or sarcoma team. See
> [MEDICAL_DISCLAIMER.md](./MEDICAL_DISCLAIMER.md).

## Licence

Code is under [LICENSE](./LICENSE) (Apache-2.0). Cited medical literature belongs to its original
publishers; this repository links to sources rather than reproducing them.
