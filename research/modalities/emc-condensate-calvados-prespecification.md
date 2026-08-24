---
id: DOC-EMC-CONDENSATE-CALVADOS-PRESPEC
title: "Prespecification — CALVADOS single-chain simulation of EMC's retained 5' partner segments"
level: L4
kind: prereg
status: immutable
canonical_for: [emc-condensate-calvados-arm]
purpose: >
  Fix, before any simulation runs, the exact quantity read out, the constructs and their controls,
  what counts as a real difference against run-to-run variation, and what result makes this arm a
  clean NEGATIVE rather than a shrug.
scope: >
  The CALVADOS 2 single-chain arm only. The slab phase-coexistence arm and the multi-domain
  (CALVADOS 3) arm are named in section 10 and are NOT run under this document.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-24
last_verified: 2026-08-24
---
# Prespecification — CALVADOS single-chain simulation of EMC's retained 5' partner segments

**Frozen 2026-08-24, before any construct in section 3 was simulated.** Nothing below may be changed
after a run lands; an amendment is an appended, dated, numbered block stating what changed and why.
The executable half of this document is
[`emc_condensate_calvados.py`](./emc_condensate_calvados.py) — the construct set, the protocol, the
guards and the scorer are code, frozen in the same commit as this file, so the rules cannot be
reinterpreted once numbers exist. `--selftest` asserts all of it offline, before one integration step.

---

## 1 · Why this arm exists, in one paragraph

[`fusion-condensate-disruption-paper.md`](../manuscripts/fusion-direct/fusion-condensate-disruption-paper.md)
argues that the fusion's aberrant biomolecular-condensate behaviour is the one handle that is
fusion-selective by construction, because wild-type NR4A3 has no EWS-type prion-like low-complexity
domain at all. Its entire first-party evidence is amino-acid composition counting, which its own
artifact correctly calls a sequence-derived proxy and not a condensate measurement. The field-standard
residue-resolution instrument for that class of claim has never been run here:
[`new-evidence-routes.md` §4](../manuscripts/program/new-evidence-routes.md) records `CALVADOS` and
`Mpipi` at **zero matches repo-wide**. This arm runs the single-chain half of CALVADOS — the half whose
founding result is that single-chain conformational properties inform the model's phase behaviour — over
the retained N-terminal segments of EMC's reported 5′ partners, and asks whether the model separates
them.

**The claim worth chasing is partner stratification, not "the EMC fusion".** EWSR1 is the commonest
partner, TAF15 the second, and TCF12 is not a FET protein at all — computed rather than asserted in
[`emc-fet-construct-designs.json`](./emc-fet-construct-designs.json) → `tcf12_negative_control`. A
phase-behaviour model makes a *differential* prediction across those chimeras. That is a statement about
the disease rather than about our engine, and a wet lab that is not ours could falsify it.

---

## 2 · The exact quantity read out

| | quantity | how |
|---|---|---|
| **PRIMARY** | **ν**, the Flory scaling exponent of the single chain | `calvados.analysis.fit_scaling_exp` on the post-equilibration trajectory, unmodified library code |
| secondary, reported, never gated | R_g (mass-weighted), R_ee, R_g/√N, ν over the second half of the trajectory | as in `calvados.analysis`, with R_g recomputed locally for the reason in §6 |

**Direction of effect, registered:** *lower* ν means a more compact chain, which is the direction
CALVADOS associates with greater phase-separation propensity. One-directional predictions are registered
per construct in `emc_condensate_calvados.build_constructs()`.

**Why ν and not R_g.** The constructs differ in length **by design** — the reported junctions differ, so
the retained segments differ. R_g cannot be compared across N. ν is length-normalised by construction
(R_g ∝ N^ν), which is exactly why it is the primary readout and R_g is not.

**What ν is not.** ν is a single-chain conformational observable. This arm does not measure and does not
report a saturation concentration, a phase diagram, condensate formation in a cell, or any statement
about efficacy, selectivity in a patient, safety, a therapeutic window, or clinical readiness. **A
difference in ν between two retained partner segments is a difference in ν between two retained partner
segments.** The link from single-chain properties to phase behaviour is the *model's* premise, cited as
the model's premise; it is not something this arm measures.

---

## 3 · Constructs and controls

All sequences are verbatim prefixes of sequences already committed to this repository
([`fet-sequences-cache.json`](./fet-sequences-cache.json) and
[`emc-construct-inputs.json`](./emc-construct-inputs.json)), or deterministic, seeded transforms of one.
**Every boundary is read from a committed artifact at run time, never typed** — asserted by guard group
G1. ⭐ **TCF12 needed no fetch**: both an Ensembl (706 aa) and a UniProt (682 aa) TCF12 sequence were
already in `emc-construct-inputs.json`, measured 2026-08-24 rather than assumed.

| id | window | N | role | n | registered prediction |
|---|---|---:|---|---:|---|
| `E264` | EWSR1 1–264 | 264 | TEST · FET | 5 | more compact than `C264` |
| `E360` | EWSR1 1–360 | 360 | TEST · FET | 5 | more compact than `C360` |
| `T161` | TAF15 1–161 | 161 | TEST · FET | 5 | more compact than `C161` |
| `C264` | TCF12 1–264 | 264 | TEST · non-FET | 5 | less compact than `E264` |
| `C360` | TCF12 1–360 | 360 | TEST · non-FET | 5 | less compact than `E360` |
| `C161` | TCF12 1–161 | 161 | TEST · non-FET | 5 | less compact than `T161` |
| `N260` | NR4A3 1–260 | 260 | CONTROL · wild-type | 5 | less compact than `E264` |
| `F212` | FUS 1–212 | 212 | CONTROL · third FET gene | 5 | in the FET range, not the TCF12 range |
| `E264_scr1..3` | `E264` shuffled, seeds 20260824/25/26 | 264 | NULL · composition | 2 each | ν differs from `E264` |
| `C264_scr1..3` | `C264` shuffled, same seeds | 264 | NULL · composition | 2 each | ν differs from `C264` |
| `E264_E15` | `E264`, 15 % of positions → Glu, seed 20260827 | 264 | INSTRUMENT | 3 | strictly *more expanded* than `E264` |

The construct and run **counts are derived, never typed here** — they are `n_constructs` and
`n_runs` in [`emc-condensate-constructs.json`](./emc-condensate-constructs.json), which
`--manifest` regenerates along with every sequence and its SHA-256.

### 3.1 · Why the constructs are these windows and not the obvious ones

- **`E264` is double-anchored.** It is simultaneously the committed AlphaFold LC/disorder window for
  EWSR1 (mean pLDDT 38.8, 98.1 % of residues below 50,
  [`nr4a3-structure-assessment.json`](./nr4a3-structure-assessment.json)) and the retained 5′ segment of
  the reported EWSR1::NR4A3 **type 2** junction.
- **⛔ The commonest reported junction is NOT type 2, and the type-1 segment cannot be run as an IDR.**
  [`emc-fet-construct-designs.json`](./emc-fet-construct-designs.json) records **type 1 (EWSR1 exon 12 ::
  NR4A3 exon 3) as the commonest reported transcript type**, retaining **EWSR1 1–431** — and the same
  repository's AlphaFold assessment places EWSR1's **folded RRM at 361–442**. So the type-1 retained
  segment runs 71 residues into a folded domain. CALVADOS 2 treats every residue as disordered, so
  running EWSR1 1–431 under it would be a model misuse. `E360` is therefore the type-1 segment
  **truncated at the last residue before the committed RRM start**, and the multi-domain reading of the
  full type-1 segment is named in §10 and **not run here**. Guard G2 asserts that no simulated window
  reaches into the RRM.
- **TCF12 arms are exactly length-matched to their FET counterparts** (G4), so chain length is not the
  between-partner variable. They are also **isoform-independent**: the two committed TCF12 sequences are
  identical over residues 1–396, and every simulated TCF12 window is shorter than that (G5). ⭐ Choosing
  360 rather than 431 removes a **real** ambiguity — G5 also asserts that a 431-residue TCF12 window
  *would* differ between the isoforms, so this is not a hypothetical being dodged.
- **`F212` stops at FUS's RG-free ceiling**, read from
  [`emc-fet-idr-census.json`](./emc-fet-idr-census.json) rather than chosen.
- **`N260` is the manuscript's own internal negative control** — NR4A3's own disordered AF1 — re-asked at
  the phase-behaviour level instead of the composition level.

### 3.2 · Window eligibility, fixed before the fetch

A window enters the CALVADOS 2 single-chain arm only if AlphaFold predicts it predominantly disordered:
**at least 75 % of its residues below pLDDT 50**, the disorder proxy this repository already uses and
cites. The pLDDT for every window is fetched ($0, AlphaFold DB) and **reported whether or not it passes**, to
`research/modalities/emc-condensate-window-eligibility.json`. The threshold is fixed here and in
`emc_condensate_calvados.PLDDT_DISORDER_FRACTION` **before the fetch** — this document and that constant
are committed in one commit, and the eligibility artifact lands in the next one, so the ordering is a
fact in the git history rather than an assurance in prose. It gates *eligibility for this model*, never
the result.

⚠ **This is the one place a threshold could decide an answer, so it is stated as a limit rather than
hidden.** If a TCF12 window fails eligibility, the FET-vs-non-FET comparison at that length is reported
as *not testable under this model* — not as a difference.

---

## 4 · Sampling standard, fixed up front

**The protocol is the CALVADOS package's own shipped single-IDR example, unmodified**
(`examples/single_IDR/prepare.py`): CALVADOS 2 residue parameters, 293.15 K, 0.19 M ionic strength,
pH 7.5, 10 fs timestep, **1010 frames × 7000 steps**, first 10 frames discarded, charged termini, CPU
platform. The one deviation is the box, and it was **measured to be free**: 150 nm rather than 50 nm cost
48.5 s against 48.8 s for 20 000 steps of a 431-mer at four threads, and it removes any chance of a chain
interacting with its own periodic image. The box is identical for every construct, so it is not a
between-construct variable.

**5 replicates** for every TEST and CONTROL construct, each with a distinct, deterministic seed derived
from `sha256(construct/replicate)`; distinctness is asserted by G8 and re-checked against the actual run
records by the scorer. Replicate SD is the error bar, per the programme's stated field standard.

⛔ **Scoped up front and not to be extended reactively.** More sampling, more replicates or tighter
confidence intervals are **not** to be added after seeing the numbers. If the standard-rigour result is
ambiguous, the honest report is that it is ambiguous.

---

## 5 · What counts as a real difference

Let each construct's value be the **mean of its replicate ν**, and let **σ_pool** be the pooled
within-construct replicate SD over the eight TEST and CONTROL constructs.

**Rule D1 — separation.** Two constructs are SEPARATED iff **both** hold:

1. |Δν̄| ≥ **3 σ_pool**, and
2. their replicate **ranges are disjoint** (`max(A) < min(B)` or `max(B) < min(A)`).

**Rule D2 — permutation, reported alongside.** Exact two-sided permutation test on the replicate ν,
statistic |Δ mean|. At 5 vs 5 there are **252 arrangements**, so the attainable floor is p = 0.0079.
Borrowing the powered-design condition already adopted in
[`selcal-xtal-prereg.md`](./selcal-xtal-prereg.md) — *minimum attainable p ≤ α/3* — the primary design
**is powered** (0.0079 ≤ 0.0167) and this is asserted by G10 rather than asserted in prose.
⛔ Any 3-vs-3 comparison has a floor of exactly 0.05 and is declared **UNDERPOWERED here, in advance**;
such comparisons rest on D1 alone and never on a p-value.

**Families and multiplicity.**

- **PRIMARY family — three length-matched FET-vs-TCF12 pairs**: `E264`/`C264`, `E360`/`C360`,
  `T161`/`C161`. Holm–Bonferroni across those three at α = 0.05.
- **SECONDARY, reported uncorrected and labelled**: `E264`/`T161`, `E360`/`T161`, `E264`/`E360`,
  `E264`/`N260`, `T161`/`N260`, `E264`/`F212`, `F212`/`C264`.

**Headline claims, each with its own gate.**

- **Claim 1 (FET vs non-FET partner):** supported iff at least one PRIMARY pair is SEPARATED under D1
  *and* survives Holm under D2.
- **Claim 2 (FET vs FET — EWSR1 vs TAF15, the clinically meaningful minority axis):** supported iff
  `E264`/`T161` or `E360`/`T161` is SEPARATED under D1. Secondary; reported as secondary.
- **⛔ No direction is registered for `E264` vs `E360`.** Extending the retained EWSR1 segment from 264 to
  360 adds both charge (expanding) and cation-π-capable arginine (compacting), and we do not know which
  wins. Declaring "no direction" up front is more honest than inventing one, and it means that comparison
  cannot be scored as a confirmation either way.

---

## 6 · When no ν is quoted at all

**INSTRUMENT_FAILED** — the arm reports the failure and withholds every ν, for any of:

- any run with fewer than **900** analysed frames (of 1000 kept);
- any construct mean ν outside the physical range **[0.30, 0.75]**;
- **`E264_E15` failing to expand relative to `E264` by 3 σ_pool** — like charges repel under the model's
  Debye–Hückel term, so this is a property of the force field, not of the biology, and its failure means
  the electrostatics are not being applied;
- a missing provenance field — CALVADOS version *and commit*, OpenMM version, platform, seed, sequence
  SHA-256, or a wall time under 60 s. **A populated field is not a measured one**, so what is checked is
  what only a real run can produce;
- replicate seeds that are not distinct within a construct.

**INCOMPLETE** — the run set does not match the frozen manifest (a missing construct, a missing
replicate, or a construct that is not in the manifest). ⛔ **This was measured missing and then added**:
before it, the scorer returned `NO_SEPARATION` — a verdict about the disease — from **zero** simulations,
and the guard meant to catch that passed vacuously through an `or`. G11 now asserts the verdict itself.

**Neither verdict is a negative result.** An absent reading is not a reading of absence.

⚠ **One upstream defect is worked around and is recorded here rather than in a commit message.**
`calvados.analysis.get_masses` mutates a pandas view in place (`analysis.py:271`, `masses[0] += 2.`),
which raises `ValueError: assignment destination is read-only` under **pandas 3.0.5**, where `.values`
returns a non-writeable array. Reproduced in two lines, and it disappears under pandas 2.3.3. The lane
therefore **pins `pandas<3`** so the library runs exactly as its authors wrote it, and R_g is recomputed
locally with an explicit writable mass array. ν — the primary readout — comes from unmodified library
code either way.

---

## 7 · ⭐ What makes this a clean NEGATIVE rather than a shrug

Four negatives, each named before the run, each a real result about the disease or about the instrument's
value, and **none of them "the run failed"**.

**N1 · `NEGATIVE_COMPOSITION_ONLY`.** For each scrambled parent, compare the parent's ν̄ against the mean
of its three composition-preserving scrambles. If **neither** parent's gap reaches 3 σ_pool, the
simulation is resolving nothing beyond amino-acid composition — and composition counting is *already* in
the manuscript. The arm would then have added a more expensive route to a number the paper already has,
and the honest report is that CALVADOS adds no new axis of evidence here. ⚠ This is scored
**independently** of separation: if partners separate *and* N1 fires, the separation is real but is a
composition effect, and must be reported as one.

**N2 · `NEGATIVE_NO_STRATIFICATION`.** No pair in the primary family separates under D1. The model says
the three chimeras' retained segments have indistinguishable single-chain conformational properties.
**This contradicts the motivation in `new-evidence-routes.md` §4 and is the most valuable single outcome
this arm can produce**, because it is a falsification of a prediction the programme was about to build
on. It gets written up as a result, not filed as a failure.

**N3 · `NEGATIVE_WILDTYPE_NOT_SEPARATED`.** `N260` — wild-type NR4A3's own disordered AF1 — does not
separate from `E264`. The manuscript's central asymmetry survives at the composition level but **fails at
the phase-behaviour level**, and the manuscript must say so.

**N4 · `NEGATIVE_FET_NOT_SPECIAL`.** None of the three length-matched FET-vs-TCF12 pairs separates, so
FET identity carries no signal on this axis. The clinical reading — that a TCF12-partnered patient is
different — would then be **unsupported by this instrument**, which is exactly the sort of thing that
should stop a route rather than decorate it.

**Any of N1–N4 closes the question this arm was built to answer, and each is publishable at its true
weight.** The one outcome that is *not* a result is INSTRUMENT_FAILED or INCOMPLETE, and §6 makes those
distinguishable from a negative by construction.

---

## 8 · Registered predictions, in one place

Every construct carries its `registered_prediction` and its `falsifier` in
`build_constructs()`; the manifest is the machine-readable copy. In prose, the whole registered
expectation is:

> The three FET-partner windows (`E264`, `E360`, `T161`, and the `F212` anchor) are **more compact** —
> lower ν — than their **length-matched** TCF12 windows and than wild-type NR4A3's own AF1; the
> composition-preserving scrambles differ from their parents; and the Glu-doped control expands.

⛔ **If the FET windows come back *more expanded* than TCF12, that is not a licence to reinterpret the
direction.** It falsifies the registered prediction and is reported as such.

---

## 9 · Claim ceiling — enforced by `lint_claims` and by CLAUDE.md

No efficacy. No selectivity in a patient. No safety. No therapeutic window. No clinical readiness.
Nothing here is a drug, a drug candidate, or evidence about a person. **A phase-behaviour difference
between two chimeras is a phase-behaviour difference between two chimeras** — and in this arm it is not
even that: it is a *single-chain conformational* difference between two retained partner segments, from
which the model, not this measurement, infers phase behaviour.

---

## 10 · What is deliberately NOT run under this document

- **The slab phase-coexistence arm** (multi-chain, direct-coexistence, a saturation concentration).
  It is the arm that would let the word "phase behaviour" be used about a measurement rather than about a
  model's premise. It needs a GPU and is a real-dollar spend, so it is **priced separately and put to
  trimcrae before anything is rented**; the cost bases live in
  [`pricing.md`](../compute/pricing.md) and are not restated here. **Nothing in this document authorises
  it**, and the single-chain arm is complete without it.
- **The multi-domain (CALVADOS 3) reading of the full type-1 segment** (EWSR1 1–431, including the
  truncated RRM), and of the full-length chimeras, which need AlphaFold coordinates and domain restraints
  rather than sequence alone. Named in §3.1; not run; not claimed.
- **Mpipi**, the other member of the model family. A second force field would be a genuine new axis, and
  it is a separate decision.

---

## 11 · Amendment log

*(an amendment is appended here, dated and numbered, and never edited in place)*

### Amendment 1 — 2026-08-24, before any production run — the ν gate conflated *compact* with *broken*

**What changed.** §6's single range `[0.30, 0.75]` was doing two jobs at once: deciding whether a fit
could be believed at all, and deciding whether a value was surprising. Those are split:

| | range | consequence |
|---|---|---|
| `NU_BROKEN_RANGE` | ν ∉ (0.15, 0.95) | **INSTRUMENT_FAILED** — no fit of a real trajectory lands there, so nothing is quoted |
| `NU_EXPECTED_RANGE` | ν ∉ [0.30, 0.75] | the value **stands**, the construct is **flagged**, and its convergence diagnostic must be quoted with it |

A convergence diagnostic is also now **required output** rather than an incidental field: ν on the
second half of each trajectory against ν on the whole post-equilibration trajectory. If more than 20 %
of runs drift by more than the pooled replicate SD, every ν is labelled **PROVISIONAL** — reported,
never withheld.

**Why, and the evidence.** The polymer **globule limit is ν = 1/3**, and a finite compact chain can fit
*below* it. A lower bound of 0.30 would therefore have withheld a genuinely compact FET LC domain as an
instrument failure — the single most likely real result this arm can produce, discarded by a threshold
meant to catch broken integration. The conflation was exposed by a **local shakeout** on TAF15 1–161 at
reduced sampling (84 000 steps, 110 analysed frames, wall 93 s): ν = 0.337 over the whole trajectory and
0.289 over its second half, a chain still collapsing out of its initial configuration. **No production
number exists at the time of writing** — this shakeout used a deliberately shortened trajectory, is not
a construct in §3's sense, and no value from it enters any claim.

⚠ **Read this as what it is: a gate being loosened, which is the dangerous direction.** Two things bound
it. The independent reason is a textbook polymer fact available before any result rather than a
rationalisation built around one. And the **reporting is strictly stricter than before** — a value
outside the expected range previously vanished with the whole panel and now must be published together
with a convergence delta. What was removed is a withholding, not a check.

**Also fixed in the same commit, and it is a plain bug rather than an amendment:** the analysis record
never populated `platform`, which the scorer requires — so **every production run would have returned
INSTRUMENT_FAILED**. `platform`, `threads`, `steps`, `wfreq`, `temp` and `ionic` are now read back from
the config each run actually used. A required provenance field that nothing writes is the same defect as
one nothing checks.
