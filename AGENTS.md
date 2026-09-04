---
id: DOC-AGENTS
title: How to maintain this repository
level: —
kind: runbook
status: live
canonical_for: [medical integrity rules, literature ingestion, figure standards, human-in-the-loop rules]
purpose: The maintenance guide for anyone — human or agent — doing work in this repository.
scope: >
  Practices and non-negotiable rules. It is NOT the plan (that is the roadmap), NOT the architecture
  (that is systems/ARCHITECTURE.md), and NOT the standing agent rules (that is CLAUDE.md).
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: 2026-09-04
related: [DOC-ARCHITECTURE, DOC-CONVENTIONS, DOC-MIGRATION]
---

# Agent entry point

This is a computation-only EMC research program with no wet lab and a limited budget.
The objective is useful evidence that could improve patient outcomes.

Read [the operating protocol](research/autonomy/OPERATING_PROTOCOL.md) first. It is the active
work-selection, coordination, and review procedure for Codex and Claude. The current priority is
the EMC ASO package for Nucleic Acid Therapeutics; its Qeios version history remains with the user.

## Scientific integrity

- Never invent medical facts, statistics, sources, patient data, experiments, or test results.
- Every claim must be traceable to an actual source or reproducible computation. Distinguish
  prediction, association, and experimental validation; preserve limitations and negative results.
- No computational result establishes clinical efficacy, safety, or a therapeutic window.
- Preregistrations are immutable. Append dated amendments; do not rewrite the original hypothesis.
- Read [evidence policy](systems/POLICY-evidence.md) before editing the clinical registry. Keep
  synthetic data explicitly labeled and primary/secondary provenance distinct.
- Generate figures from committed data with a committed script; inspect the result. State units,
  sample size, uncertainty definition, and scope. Do not fabricate a measurement in a graphic.

## Read only what the task requires

| Task | Source |
|---|---|
| ASO release work | `research/manuscripts/aso/`, existing review seats and hardening state |
| Scientific program model | `systems/ARCHITECTURE.md`, `systems/graph/` |
| Degrader research | `research/manuscripts/nr4a3-program-map.md` |
| Legacy remote cycle | `.claude/skills/research-loop/SKILL.md` |
| Review or final verification | `.claude/skills/paper-hardening/SKILL.md` |
| Commit/publication checks | `.claude/skills/repo-gates/SKILL.md` |
| Publication permission | `research/autonomy/publication-authority.json`, actual enforcers |

## Working agreements

Use separate worktrees for writers and one coordinator for integration/shared queue state.
Run relevant checks and the normal preflight once the tree is settled. Regenerate systems views
after graph changes. Preserve provenance and pinned-quantity correction records. Do not open a
pull request unless asked. Report what changed, actual validation, unresolved issues, and whether
anything is really running. Historical instructions are references, not extra acceptance gates.
