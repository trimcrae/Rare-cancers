---
id: DOC-CONTRIBUTING
title: Contributing
kind: runbook
status: live
canonical_for: [how to add a research object, contribution rules]
purpose: How to add to this repository so the addition is checkable, traceable and does not drift.
scope: >
  Contribution mechanics for the research platform. The non-negotiable medical-integrity rules live in
  AGENTS.md, the evidence contract in systems/POLICY-evidence.md, and the object model in systems/ARCHITECTURE.md.
audience: [maintainers, collaborators, autonomous research agents]
date: 2026-08-05
last_verified: 2026-08-05
related: [DOC-AGENTS, DOC-ARCHITECTURE, DOC-CONVENTIONS]
---

# Contributing

Contributions from clinicians, researchers, and anyone who has read the literature carefully are
welcome. The most valuable contribution is usually a **source we have missed** or a **correction with a
citation**.

⛔ *Superseded, retained: this file used to describe contributing to a patient-facing website — adding
support groups, specialist centres and per-cancer JSON pages. That site is retired and deleted.*

## The one rule that matters most

**Everything clinical must be true and sourced.**

- A real, resolvable identifier for every study, statistic and clinical claim — a PMID, PMC ID or DOI,
  not a URL alone.
- Never invent numbers or round from memory. Use ranges across real studies.
- Never present sample or illustrative data as real. Non-real data is flagged `SAMPLE_SYNTHETIC` and
  bannered.
- Never remove or soften a medical disclaimer or a stated limitation.
- Never read a number out of a review and present it as the primary study's — set
  `provenance: "secondary"` and record `primaryRef`.

You do not need to be a clinician. Most useful contributions are about *finding and linking* good
sources, not giving advice.

## Easy ways to help, with no code

Open an issue with any of:

- **A study we are missing** — especially an EMC series with explicit event counts, or any EMC
  functional-genomics or expression dataset. That last one is the repository's single biggest
  rate-limiter; see [`systems/views/registers/technologies.md`](./systems/views/registers/technologies.md).
- **A correction**, with the source that establishes it.
- **A capability that has landed** — a method one of the registered technology dependencies is waiting
  for. Each says, in searchable words, exactly what would count.
- **An offer of bench access.** Several routes are fully specified experimental proposals waiting only
  on someone with cells; see [`systems/views/readiness.md`](./systems/views/readiness.md).

## Adding to the model

The model is `systems/graph/*.json`. Everything under `systems/views/` is **generated** — editing a view
directly will fail the build, which is the point.

```bash
# 1. edit the relevant systems/graph/*.json
# 2. regenerate the views
python3 systems/systems_check.py --write-views
# 3. check invariants, pointer resolution and view drift
python3 systems/systems_check.py --check
```

Every object must carry the standard fields — purpose, inputs, outputs, state, assumptions, limitations,
blockers, provenance and next action ([`systems/ARCHITECTURE.md`](./systems/ARCHITECTURE.md) §5). The
checker rejects a partially specified object rather than accepting a vague one, and the identifiers and
controlled vocabularies are closed ([`systems/CONVENTIONS.md`](./systems/CONVENTIONS.md)).

Three rules catch most mistakes:

1. **One fact, one home.** If you are typing a number that already exists somewhere, point at it instead.
2. **A claim can never be stronger than the instrument underneath it.** An instrument that has not
   recovered a known answer cannot be cited as support — and "the control failed" and "there is no
   control" are different facts, neither of which is support.
3. **A superseded number is registered, never silently dropped.** Add it to `pinned-figures.json` in the
   same commit as the correction, so CI can find the copies you missed.

## Adding clinical evidence

Clinical data lives in [`research/data/emc-clinical-registry.json`](./research/data/emc-clinical-registry.json)
and is governed by [systems/POLICY-evidence.md](./systems/POLICY-evidence.md), which specifies the citation structure, what may be
pooled with what, how to represent disagreement, and how to handle data age.

```bash
node scripts/validate-registry.mjs      # the evidence contract; also gate 2 of preflight
```

⚠ **Two pooling methods exist and are not interchangeable** — crude denominator-weighted proportions with
Wilson intervals for simple proportions, and a random-effects model for the manuscript. POLICY-evidence.md §2
says which is which and why quoting one where the other is meant is a real error.

## Before you commit

```bash
./scripts/preflight.sh          # THE gate — its exit code cannot be masked
```

## Style

- Plain, precise language. Define jargon once, then use it consistently.
- State limitations in the same place as the result, not in a separate caveats section.
- Keep the model layer dependency-free — pure stdlib Python and plain JSON.
- Prefer adding a check over adding a convention. A convention that is not enforced decays; this
  repository has the receipts.
