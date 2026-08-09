---
id: DOC-TAX-MODALITY
title: Modality-class taxonomy — the census of what oncology can do, and what reaches EMC
level: L0
kind: policy
status: live
canonical_for: [modality band enum, modality group enum, EMC applicability verdict vocabulary, prior_coverage vocabulary]
purpose: >
  Define a modality class as a first-class object — a category of cancer treatment that exists
  somewhere in oncology, recorded independently of whether this program ever considered it — and fix
  the vocabulary that grades each one against EMC.
scope: >
  The vocabulary and the rules that keep a census distinguishable from a search. Instances live in
  systems/graph/modalities.json. This file grades no individual class and names no route.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-09
last_verified: 2026-08-09
related: [DOC-TAX-TECHNOLOGY, DOC-TAX-BLOCKERS, DOC-ARCHITECTURE, DOC-CONVENTIONS]
---

# Modality-class taxonomy

> **Role:** the one home of the `band`, `group`, `verdict` and `prior_coverage` vocabularies.
> Instances live in [`../graph/modalities.json`](../graph/modalities.json), rendered to
> [`../views/modality-census.md`](../views/modality-census.md).

---

## 1 · Why a census is a different instrument from a search

This repository has run three sweeps for treatment options beyond its own board, and each was a
**search**: it returned what it queried for. A search can only ever report what it found, so its
silence is ambiguous — a class absent from its output may have been considered and dismissed, or may
never have been pointed at. The two are opposite situations with opposite remedies, and no prior
document could separate them.

The 2026-08-07 sweep measured the cost of that ambiguity from the inside. Four whole categories had
been invisible to every previous search — not rejected, never queried — and its own diagnosis was
**instrument shape** rather than oversight: the portfolio's searches were molecular-modality-centric,
so physical and locoregional treatment, the matrix as an address rather than an obstacle, non-cancer
diseases sharing the phenotype, and treatment strategy as opposed to new agents were all outside the
shape of every query anyone had written.

A **census** enumerates the space first and grades second. Its product is a denominator, and a
denominator is what makes absence auditable: with one, *"nobody has looked at this"* is a field you
can query and a checker can verify; without one it is a recollection, and recollections are exactly
what this repository has repeatedly found itself re-deriving.

⚠ **A census is not a claim to completeness of oncology.** It is a claim that the enumeration is
explicit, that every prior ruling is accounted for, and that the residue is named. Rows will be
missing; the census is built so that adding one is a cheap edit rather than a re-derivation.

---

## 2 · Bands

The band records **what kind of intervention** the class is, and exists because three of the four were
structurally invisible before.

| band | means |
|---|---|
| `drug_mechanism` | a molecule or biologic acting through a stated mechanism |
| `delivery_and_conjugate` | how an agent is carried, targeted, formulated or activated — often the difference between an unreachable target and a reachable one |
| `physical_locoregional` | a beam, a machine, a procedure or a regional delivery route rather than a systemic agent |
| `strategy_and_architecture` | not a new agent: scheduling, sequencing, eligibility, trial design — changes to what a patient actually receives |

## 3 · Groups

Nineteen, and they partition the census: `cytotoxic · hormonal_nuclear_receptor · kinase_inhibitor ·
enzyme_inhibitor_non_kinase · ppi_and_undruggable · degrader_induced_proximity · nucleic_acid ·
gene_and_cell_engineering · antibody_and_antibody_like · cell_therapy · vaccine_active_immunization ·
immune_modulation · microenvironment_and_stroma · metabolic_and_dietary ·
radiopharmaceutical_and_radiation · physical_device_locoregional · host_directed_and_repurposed ·
delivery_and_formulation · strategy_and_trial_architecture`.

A group is **a place to look, not a claim**. Two rows in one group routinely end in opposite verdicts,
and a group with every row excluded is a finding rather than a filing error.

## 4 · Verdicts

| verdict | means | the row must carry |
|---|---|---|
| `on_board` | an existing route already covers this class | `route` — an `RT-*` that exists |
| `in_clinical_use` | already given to EMC patients — the incumbent arsenal | the record it rests on, in `prior_ref` |
| `already_rejected` | someone here already settled it | `prior_ref` — the document that owns the ruling |
| `excluded` | **this census** is what closes it | the argument, in `rationale`, because here is its only home |
| `candidate` | it survives, and it is new | `zero_dollar_next_step` |
| `parked_capability` | plausible, waiting on something absent | `revisit_trigger` — a `TECH-*` |
| `not_applicable` | the class has no EMC-relevant instance at all | the reason, in `rationale` |

⛔ **`already_rejected` and `excluded` are separate on purpose, and collapsing them breaks rule 1.**
Roughly fifty classes already carry a ruling in a prior document. For those the row's whole job is to
**point**, and restating the reason would create a second home for it that drifts. Where this census
is itself the closer, the reason belongs in the row because the row is its only home. A single value
covering both would force one of those two failures.

⭐ **`in_clinical_use` is the denominator's denominator.** The question that produced this census
described EMC's options as *"a pretty small arsenal"*, and how small is a measurement rather than an
impression — so the classes patients actually receive are counted here alongside the ones they do not.
⛔ **It grades availability, never benefit.** A class is `in_clinical_use` because the record says it
is given, and that says nothing whatever about what it achieves.

⚠ **`not_applicable` is the weakest verdict and is used sparingly.** "No instance exists" is a claim
about oncology, not about EMC, and it ages badly. Where the honest statement is *"nothing addresses
this in EMC today"*, that is `excluded` or `parked_capability`, not `not_applicable`.

## 5 · Prior coverage

`searched_before` · `never_searched`. **This is the field the census exists to produce.**

It is orthogonal to the verdict, and the orthogonality carries the finding: a class can be
`never_searched` and `excluded` — nobody looked, and now that someone has, it does not reach — or
`never_searched` and `candidate`, which is the residue the three prior searches could not have
returned. `searched_before` requires a `prior_ref` that resolves, so the claim that a class was
covered is checked rather than remembered.

## 6 · The rules that keep the register honest

1. **The axis is modality, never target.** `antibody-drug conjugate` is a row; a particular antigen
   directed through one is not. Target questions enter only as `requires` preconditions, and the
   artifacts that own them stay their home.
2. **A verdict points or argues, never both.** See §4.
3. **`on_board` names a route or it is not a coverage claim.** An unverifiable assertion that the board
   already handles something is the specific failure this collection was built to make impossible.
4. **A `never_searched` row may not be quietly downgraded.** Changing it to `searched_before` requires
   naming the document that searched it, which means the flag can only be cleared by evidence.
5. **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness** — for any
   class, in any verdict, including the ones that survive.
