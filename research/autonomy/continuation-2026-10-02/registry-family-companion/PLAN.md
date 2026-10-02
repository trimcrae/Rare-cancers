---
id: DOC-CHECKPOINT03-REGISTRY-FAMILY-COMPANION
title: Frozen plan for a source-context registry family companion
level: cross-cutting
kind: memo
status: live
purpose: Test whether explicit outcome-context families can accompany literal category roles without changing accepted normalization.
scope: The accepted 575-unit replay artifact and 27 reviewed immune-context units; standard-library companion and synthetic conformance, not a new registry scan.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: unverified
---

# Question and frozen inputs

Can a separate conservative companion attach explicit outcome-scoped family identity and literal category roles while preserving ambiguity, confirmation context, source coordinates, all measurements, denominators and accepted normalization?

The input is the already accepted 251939-byte artifact ZIP, ID11231565922, run37017553101, job110872050056, SHA256 `57d104bd9f9e101c82c0ecf90e50837b084eafd165a0d12bb8faaecf3fed0deb`. `inputs.json` binds the exact ZIP and member byte hashes, plus the separately reviewed 27-unit oracle. No archived raw CT.gov corpus or current registry API is needed. The complete outcome objects, accepted rows and comparisons occupy about 4.2 MB uncompressed. The reviewer reference is independent of this companion's logic; its 27 unit keys, named families, literal vectors and denominators were frozen before implementation.

Preparation inspected and hashed the accepted ZIP in memory. It did not execute the companion or its synthetic tests. Root owns the first test and saved-corpus replay. Code and plan are frozen for that run; assigned/ambiguous/unknown counts remain unknown until the run completes.

## Companion contract

`family_companion.py` contains no trial-ID branches. It recognizes a finite list of explicit family names, optional modifiers and source-written versions in title/description text. Description mentions need an assessment cue or a definition; bare bibliographic mentions do not suffice. Conflicting family names, conflicting versions or detected negation remain ambiguous. Missing names remain unknown, even when category labels carry an i/ir prefix. This is deliberately incomplete lexical recognition, not a natural-language adjudicator; unknown does not prove absence of a source definition.

Each family is scoped to `(NCT ID, complete outcome JSON SHA256)`. Unit keys additionally retain literal class index and outcome-local group ID. Evidence includes source-field character offsets, exact matched strings, surrounding literal sentence, original physical source coordinates, and full outcome literals. Reader, confirmation, time frame and population context are preserved as source prose rather than converted to a clinical equivalence assertion.

Category roles are lexical labels inside the source-named family. Unconfirmed and confirmed progression are separate UPD/CPD roles and are never collapsed into PD. Qualified or contradictory labels, duplicate aliases and label/context mismatch remain explicit. Missing/noninteger cells are never imputed. A four-cell family map is emitted only with one integer CR/PR/SD/PD cell each and no duplicate/mismatched or separate progression-state cells. No clinical response rate is computed. Family version may be absent without inventing one.

Ordinary-label qualification remains exactly the accepted utility's field. The companion copies the complete accepted row and checks against mutation, while emitting semantics in separate fields. Full outcome objects are also emitted unchanged. A source explicitly using modified irRC with unprefixed labels stays in that family; it is not relabelled ordinary RECIST. Pooling is disabled regardless of shared family spelling.

## Root cloud invocation

From the companion directory, with the accepted ZIP staged by the coordinator:

```sh
python3 -m unittest -v test_family_companion.py
python3 family_companion.py --zip /tmp/registry-full-replay.zip --out /tmp/checkpoint03-registry-results
```

The CLI defaults to adjacent `inputs.json` and `reviewed-27.json`; both can be supplied explicitly. No network, dependencies, runtime install, raw-corpus scan or Git command occurs. A fresh output directory is required. Root should apply a five-minute job timeout and reserve at least 64 MiB for this lane. The companion enforces a two-minute processing deadline, exact ZIP/member sizes and hashes, duplicate-member rejection, canonical outcome hash identity, unique575-unit joins, and a 16 MiB cap per output (three outputs, maximum48 MiB). It reads ZIP members in memory and never extracts arbitrary paths.

## Conformance and acceptance

Fourteen synthetic test methods cover absent context, suffix-only rejection, versionless identity, explicit/conflicting versions, conflicting families, the unprefixed-label modified-irRC counterexample, longest-name matching and literal evidence offsets, separate UPD/CPD states, qualified-label preservation, duplicate aliases, immune-label/ordinary-context conflict, negated and bibliography-only mentions, unchanged literals/denominators, and noninteger cells. These are illustrative conformance cases, not held-out clinical validation.

The replay must cover exactly575 accepted unit identities and preserve the accepted510 non-null unqualified-label vectors. Each of the27 independently reviewed units must agree on family name, four literal values and denominator value/scope; none may become ambiguous or unknown. Counts of assigned/ambiguous/unknown units across575 are **measured outputs, not acceptance targets**. The reviewed-unit comparison is a known-case transfer constraint, not an unseen benchmark. A discrepancy fails the process for investigation rather than changing the oracle.

Outputs: `family-companions.json` contains each literal row plus contextual fields; `outcome-literals.json` preserves all complete outcomes; `summary.json` records status counts, named-family counts, unchanged accepted qualification, all27 agreement checks and code/input hashes. Root should retain logs and these outputs. A successful run establishes computational conformance only; it cannot establish patient-level criteria implementation, population independence, cross-family equivalence, clinical benefit or a registry error rate.
