---
id: DOC-OPUS-CAMPAIGN-HOLD-MORTALITY-CAUSAL-CEILING
title: "Paper-specific hold — the mortality causal-ceiling manuscript"
level: L4
kind: memo
status: live
purpose: >
  Record the completed adverse independent final review of the mortality manuscript, the ten findings
  root accepts, and the exact conditions under which its claims may be reinstated.
scope: >
  L4. A hold and its evidence. It repairs nothing, substitutes no count, runs no producer, and
  authorises no publication act.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# ⛔ PARK_CURRENT_MANUSCRIPT — `emc-mortality-mechanisms-paper.md`

**The independent final review is COMPLETE and ADVERSE.** Root read the full 38,388-byte report,
verified its sha256, and **accepts all ten findings — three critical, six major, one moderate**.
Review completed `2026-09-08T17:22:54.318900Z`. This is a substantive scientific hold, not a request
for another formatting pass.

- **Frozen revision:** `e21841ea103560d801f4e21f64ee31a68028e232`; manuscript **36,906 bytes**, sha256
  `9d8caa38f921feeaa3457bcc6b493868594fbbeff10c8abeb7a78fb1e935849a`.
- **Report:** `review/FINAL-SCIENTIFIC-REVIEW.md`, 38,388 bytes, sha256
  `16b6974acdbe71318ca01f03fe8bc8d7adc7f6f9749670ef16e0b6abe1681a58` — verified on intake here.
- **The reviewed mortality science is FROZEN.** ⛔ No same-paper polishing cycle, new producer chain,
  replacement denominator, full re-review, source hunt or new experiment is assigned.

⚠ **Execution metadata, corrected by root and recorded as such.** The dispatch explicitly selected
`/root/mortality_final_ultra`, model `gpt-6-astra`, reasoning effort `ultra`, `fork_turns="none"`.
The report's own statement that its assignment *inherited* the parent configuration is imprecise; the
request was explicit. ⛔ This corrects the execution request only. **No backend model attestation and
no usage measurement is claimed**, the packet's transfer manifest records
`transporter_independently_verified_served_model: false`, and the original report is preserved
unchanged beside this clarification.

## The ten accepted findings

**F1 · critical · wrong disease population.** PMID **22569967**'s two deaths are in the
**myoepithelial-carcinoma** group; the followed **cellular-EMC** group was alive. Root independently
read the exact retained primary abstract and the mortality-probe context and confirms the
attribution. **The current 50 / 14 / 27 tally is therefore not a valid EMC-specific source count.**
Earlier root verification established arithmetic and documented-death status **over the stored rows
only**; it did not validate source disease membership. ⛔ **The review's 48 / 13 / 25 and 14/48 are a
ONE-EXCLUSION ILLUSTRATION, NOT an accepted replacement tally. Do not substitute those counts.**

**F2 · critical · false time and causal interpretation.** The 6.7 and 31.0 percentage-point results
are **9/134 and 9/29 over heterogeneous follow-up** — not three-year cumulative incidences and not
survival gains. **Median follow-up does not define a common horizon.** Those counts do not bound all
tumour-directed therapy or research in a previously treated cohort.

**F3 · critical · incorrect mortality estimand.** Relative survival is not a cause-specific
cumulative incidence, and `(RS − OS)/(1 − OS)` **does not partition observed deaths**, even under
favourable independent constant hazards. ⭐ Root's analytical counterexample, **recomputed
independently here**: two independent constant hazards of 0.1/year over 5 years give OS = 0.367879,
expected = relative survival = 0.606531, so the expression returns **37.754%** where the true
competing-death share is **50%** by symmetry. ⛔ **That counterexample is analytical. It is not
patient data and not an EMC estimate.** The claimed independent convergence cannot validate cause
attribution.

**F4 · major · synthetic background presented as cohort matching.** A common assumed age 55 and 66%
male is neither each cohort's demographics nor an Ederer II estimate; crude observed other-cause
proportions and synthetic expected survival are not matched rates. ⭐ **Preserve the valid
distinction between a mortality RATE and a five-year PROBABILITY** — the earlier conversion error
must not be restored. If the illustration is retained, correct the stated direction of the
expected-survival sign effect.

**F5 · major · synthesis and uncertainty.** The conventional median of the eight included values is
**21.0%**, not the upper-middle **23.0%**, and the horizons come from only **five** series. The
exclusion's numerical-singularity rationale is unsupported. ⛔ **Correcting that median would not
validate F3.** Direct registry fractions need uncertainty and their actual follow-up and population
scope.

**F6 · major · source tiers and sampling do not establish population mechanisms.** The three named
events and one named disease entity remain a **defensible description of those retained statements**.
Hepatic metastasis at death still does not assign a cause, and **non-EMC attribution is not a
non-cancer cause**. Known unsupported legacy filing tallies belong out of the primary scientific
result, and membership, death documentation, attribution, event-versus-entity, source type and
overlap must be separated. ⛔ The selected death-cue and title collection **cannot** establish the
entire literature's mechanism absence or a dominant mode of death.

**F7 · major · comparison provenance.** The stated **20.0%** diagnostic gap belongs to the
cross-series calculation, while the current within-series artifact holds **11.8%**. Correction
history, available endpoint selection and endpoint definitions are not established by matching
numeric strings. Remove the invalid residual comparison, or identify any retained illustration
accurately.

**F8 · major · overstated provenance guarantees.** The quote verifier **permits a longer supplied
string containing a retained sentence**, and the registry checker **does not bind** numerical
extraction, path, endpoint or population. ⛔ The mutation checks concern **the claimed guarantees**;
they are **not** a finding that current quotations were fabricated. Availability must include actual
dependencies and primary-source or versioned-artifact citations, and a generic full preflight would
not establish source attribution.

**F9 · major · discussion exceeds search and transfer scope.** One answered intervention question
among **eight** queried classes cannot establish exclusivity. Preserve the unresolved source
discrepancies; make **no EMC efficacy or transport claim**; ⛔ **do not retry restricted sources.** A
specified zero-hit query supports a **scoped** search result, not global absence of any published
growth-rate measurement. Non-EMC deaths are not synonymous with non-cancer deaths.

**F10 · moderate · declaration contradicts case extraction.** The study reclassifies **published
individual case descriptions**. The declaration must state public aggregate and case-report use, no
new recruitment, contact or intervention, and **no access to original individual clinical or survival
records**. ⛔ It must **not** say that no patient-level published record was used, and must **not**
invent an institutional ethics determination.

## Exact reopening conditions

- **Reinstating the quantitative central claims** requires a defensible **common-horizon
  competing-risk or excess-hazard estimand**, time and censoring information, **verified cohort
  demographics and suitable life-table matching**, and a justified synthesis.
- **Reinstating comprehensive absence or supportive-care efficacy claims** requires a **separately
  authorized** source and synthesis scope that resolves the actual uncertainty.
- ⛔ **Clean lint or different wording is not such evidence.**
- **A different, narrowly scoped selected-source reporting audit or data note** is a possible future
  author choice **only** after explicit root or author **merit** adjudication that its reduced
  contribution is useful enough. It would require coherent disease-membership and context coding,
  withdrawal of the causal ceilings and the relative-derived cause fractions, convergence and
  background-rate claims, scoped literature assertions with primary citations and dependencies, and
  corrected declarations and provenance descriptions — then focused verification of the actual
  changed claims and dependencies, once. ⛔ **This is not authorization to produce that revision now.**

## What stays closed

The original **two undocumented-death exclusions**, the **rate-versus-probability** correction, and
the sister memo's **25-specific-query / 328-general-corpus** correction remain **CLOSED** and are not
reopened by this hold.

## What this hold is not

⛔ It is not a retraction, not a publication act, and not a claim that any gate is green or red beyond
what is separately recorded. It asserts no EMC efficacy, safety, selectivity or clinical readiness.
It binds **this paper only**: no programme-wide pause follows, and no user action is required by it.
