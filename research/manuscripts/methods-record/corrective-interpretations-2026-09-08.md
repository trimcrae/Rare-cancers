---
id: DOC-MF1-CORRECTIVE-INTERPRETATIONS-20260908
title: "Dated corrective interpretations of retained records cited by the methods-record manuscript"
level: L4
kind: memo
status: live
canonical_for: []
purpose: Record, beside the manuscript that cites them, exactly which interpretations of retained records are superseded by the 2026-09-08 correction batch — without altering a single byte of the original execution outputs, result files or protocol histories.
scope: The retained records cited by degrader-methods-failure-record.md. It corrects INTERPRETATIONS only. Every original artifact named here is unchanged and remains the evidence.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---
# Dated corrective interpretations, 2026-09-08

**Why this file exists.** The independent final scientific review of the frozen methods-record manuscript
(report SHA-256 `f4a0aceec8fdea6a1da62de2dc36ef88637c6288c05f1cc7fc318b3c971b32be`; reviewed freeze
`0b965a1279c81c10d9edc054842a33446e87762e`, main SHA-256 `a9058b6c…`) found twelve places where an
interpretation went beyond the record it cited. Root accepted all twelve.

⛔ **The correct response to a wrong interpretation of a right record is not to edit the record.** Every
artifact named below is **unchanged**: the original bytes of the execution outputs, result files, verdict
files and protocol histories stand as the record of what was actually run and what was actually decided.
What is corrected is the reading. This file is the dated place that correction lives, so a reader who
arrives at the original artifact through any path finds the supersession rather than only the superseded
claim.

⚠ **A superseded interpretation is not a retracted measurement.** In every entry below the measurement
survives; what changes is the class of conclusion it supports.

---

## C1 · `selcal-verdict.json` — the recorded `NULL` is not a powered null

**Unchanged in the artifact:** `tier: "NULL"`, statistic `+0.4373`, `p 0.746753`, `p_mirror 0.255411`,
`models_per_arm` 6 and 5, `n_legs_admitted` 22, `technical_failures` 0 and 0, `n_arrangements` 462,
`min_attainable_p` 0.0021645…, and the `reason` string that calls the design adequately powered.

**Superseded interpretation:** that the reference-set floor establishes the design's sensitivity, so the
non-separation is a powered demonstration that the readout cannot see a known difference.

**Correct reading, 2026-09-08:** the attainable p floor is a **discreteness property of the exact reference
set**, not statistical power against any effect size. No effect size is established for this observable —
the panel's own module states that the E1 readout has no established quantitative link to degradation
selectivity — and the co-fold/crystal input validation the panel assumed had not been implemented before it
ran. The record supports an **executed calibration attempt that did not meet its registered directional
criterion**, with the register control state `fails`. It is not an absent control, not an absent result, and
not a powered null.

**Reopening condition:** a retained, identifiable, pre-outcome power specification in the E1 estimand with
effect-size and noise assumptions, plus input-validity evidence for the claimed readout.

## C2 · `selcal-verdict.json` / `selcal_panel.py` — the reference identity

**Unchanged in the artifacts:** `criterion._what` names **ACBI2** (Kofink *et al.* 2022); the `reference`
block establishes direction from **PRT3789** (`doi:10.1158/0008-5472.can-25-1141`) and separately quotes a
mechanism statement about the SMARCA2/SMARCA4 pair.

**Correct reading, 2026-09-08:** current scientific summaries must name **PRT3789** as the reference the
panel's own record establishes direction from, and must not present the mechanism citation as a claim about
PRT3789. The primary publication is not open access, so **no magnitude, DC50 pair or fold window is
quotable**, and none may be imported from a secondary source. ⛔ The historical criterion text is preserved
exactly as written; this entry is the correction.

---

## C3 · `nr4a3-5aks-reduction.json` — `S_err` is a two-seed dispersion, not a bound

**Unchanged in the artifact:** `S_kcal −0.1297`, `S_err_kcal 0.3264`, `S_err_kind "replicate_sd"`,
`n_seeds` 2 per species, and the `system_identity_problems` entry flagging disagreeing `n_particles` across
the four legs.

**Superseded interpretation:** that this returns a bound excluding wedge contributions of roughly
≥ 0.65 kcal/mol at "2σ", and therefore that the marginal wedge is absent.

**Correct reading, 2026-09-08:** the reducer computes a difference of species means and
`sqrt(sd_A² + sd_B²)` from **two values per species**. That is an **exploratory conditional estimate with a
between-seed dispersion, compatible with zero at the observed precision**. It is not a confidence interval,
an equivalence test, a likelihood bound or a calibrated physical-effect bound, and it does not establish
that the wedge is absent. The design's **operational completion condition** (seeds per arm) was met, which
is a statement about the design and not about the physics. Two assumptions travel with the number: the
open particle-count comparability flag (differing solvation does not by itself invalidate the physics, and
cross-species systems need not match — but the estimate may not be read as an unqualified bound while the
flag is open), and the fact that the intervention is on the **modelled ligand Hamiltonian conditional on
the chosen structures**, not on biology.

**Reopening condition:** a source-level uncertainty analysis with an explicit estimand, independence or
covariance assumptions, sampling unit, coverage or equivalence criterion, treatment of model and input
uncertainty, and a justified confidence level.

---

## C4 · `valb-triangle-reduction.json` and `valb-triangle-closure.json` — closure identifies nothing

**Unchanged in the artifacts:** `R_ternary_kcal −0.0312`, `R_binary_kcal −0.2440`, `R_kcal 0.2128`,
`error_bar_kind "NONE QUOTED AT n=1"`; and the closure artifact's own statement that endpoint-state errors
are invisible to closure.

**Superseded interpretation:** that a small residual shows the valB_mini miss is an endpoint-state error,
that sampling error is excluded, and that more sampling will not fix the miss.

**Correct reading, 2026-09-08:** the residual is **one linear contrast of six edge errors**. Errors of 1, 2
and 3 on the three oriented edges close exactly while every edge is wrong, and a conservatively structured
bias from shared incomplete sampling telescopes the same way. Because closure is **blind** to endpoint-state
error, a clean residual is not diagnostic of it. `valb-failure-propagation.json` gives power ≈ 0.63 to
detect an r0-sized path error at its own measured upper noise bound, which is not a clean exclusion, and its
three-replicate "upper bound" on the per-leg sigma is not a confidence bound on the variance. **The
repeated wrong-sign operational calibration failure stands; its cause is not identified.**

**Reopening condition:** retained evidence that separates the proposed causes, rather than another closure
identity or a repeat of the same comparison.

## C5 · `valb-failure-propagation.json` — the SD/SE ratio is not an inflation factor

**Unchanged in the artifact:** `cycle_sd_kcal 0.375`, `per_leg_mbar_se_kcal [0.097, 0.132]`,
`n_replicates 3`, and the derived `replicate_sd_over_mbar_se_measured 3.28`.

**Superseded interpretation:** that quoting a within-run MBAR standard error understates the uncertainty
"by exactly that factor".

**Correct reading, 2026-09-08:** a **cycle** is a difference of legs, so a cycle replicate SD and a
**per-leg** MBAR SE answer different questions about different estimands; an SD across replicates and the SE
of a replicate mean differ again. Three replicates do not establish a universally transferable correction
factor. **The useful warning survives**: within-run precision does not describe between-run variability or
accuracy. The exact multiplier does not. ⛔ No substitute multiplier is adopted.

---

## C6 · `nrv04-cofold-chain-forensics-2026-07-24.md` — four defects, not one

**Unchanged in the artifact:** the per-prefix chain census showing `nrv04-descriptive-v3` and
`nrv04-shakeout` affected by the 14-3-3ε contamination and `nrv04-covalent-cofold` (the completed panel's
2026-07-22 inputs) **clean**; the positional chain-split mechanism; the `warhead_only` legs' 12.44 Å tether;
and the statement that neither defect was caught by any existing test.

**Superseded interpretation:** that one "largest retraction" arose from chain ordering, units and
contaminated inputs together; that no known-answer test could catch any of them; and that persistence alone
would have made all of them correctable.

**Correct reading, 2026-09-08:** these are **distinct defects with distinct affected inputs** — contaminated
descriptive/shakeout co-folds (not the completed panel); wrong-interface post-processing on the completed
panel; an nm/Å unit error and a chain-blind reactive-cysteine search in the same class; and two
`warhead_only` legs that **simulated the wrong physical system**. The source says the **existing** tests
missed them, which is not the same as no test being able to; its own fixes are such tests. Persisted
trajectories would have permitted the interface readouts to be **rescored**; they could not have repaired
the wrongly tethered legs.

## C7 · `nrv04-result-forensics.json` — the census is scoped to its surveyed prefixes

**Unchanged in the artifact:** two surveys, `nrv04-covalent-results/` and
`nrv04-covalent-results-chainfix/`; 17 `leg_result` records; `trajectory_objects_found: 0` in both
`recompute_verdict` blocks.

**Correct reading, 2026-09-08:** this supports a **retrospective conclusion about the surveyed prefixes**.
It is not a proof about every possible external copy of the data, and it is not evidence about any prefix
that was not surveyed.

---

## C8 · `r5-cross-method-cavity-attribution.json` — the pose disagreement is mixed

**Unchanged in the artifact:** `rollup` with `n_systems 6`, `n_gradeable 5`, `n_same_cavity 4`,
`n_different_cavity 1`, and the note that an ungradeable system is excluded from the denominator rather than
scored as agreement.

**Superseded interpretation:** that the cross-method disagreement decomposes as *same location, different
orientation*.

**Correct reading, 2026-09-08:** **4 same-cavity and 1 different-cavity among 5 gradeable systems, with 1
ungradeable.** The two sub-pockets are 9.853 Å apart and both lie inside the search sphere both engines were
given, and the cavity call is **receptor-conformer dependent** — so neither an orientation-only nor a
location-only reading holds across the census. Neither method is thereby shown correct or wrong. ⛔ The
second method's known-answer arm remains **zero gradeable of twelve listed pairs**, split **2 R2b
exclusions / 6 `dock.prm` UNRUN / 1 fetch refusal / 3 alignment refusals**, with six actual cross-method
pose comparisons executed.

## C9 · `results/nr4a3-decoy/-mmgbsa/nr4a3-mmgbsa.json` — a call rate, not a false-positive rate

**Unchanged in the artifact:** 38 decoys, 22 with a positive minimum margin, and the verdict census.

**Superseded interpretation:** a "within-repository false-positive rate"; an excluded design class; and the
claim that a signal smaller than its own noise cannot be recovered by any downstream method.

**Correct reading, 2026-09-08:** **22 of 38 is a positive-call rate among these selected decoys under this
scoring configuration.** The archive supplies computed scores and computational labels, not measured NR4A
negative labels, and the calibration module states the distribution depends on the receptor frames used.
The finding is evidence **against reading `margin > 0` alone as a selectivity verdict**, and is not evidence
about downstream methods or about any design class.

## C10 · `r3-generation-frame-harmonized.json` — a gate failure, not an impossibility

**Unchanged in the artifact:** `verdict GATE_A_FAIL_BELOW_DSTAR`, `druggability 0.259`, `d_star 0.53`.

**Correct reading, 2026-09-08:** the failure of **one operational screening threshold on one receptor
frame**. It is not a statement about binding, ligand-induced states, or every molecule generated there, and
the universal reading *"a candidate cannot be better than the pocket it was designed into"* is withdrawn.

## C11 · `nr4a3-5bt-signature.json` — a descriptor-scoped zero

**Unchanged in the artifact:** `sentence_replicated`, 16 models per arm, the descriptor's own
`_proxy` note ("N/O heavy-atom pair within 3.5 Å; no hydrogens are placed in these deposits"), and the
single recovered known-answer position.

**Correct reading, 2026-09-08:** **zero qualifying sequence-variable heavy-atom polar contacts under this
descriptor, in these 16 generated models.** The known-answer recovery is a narrow in-sample development and
harness check — one contact, one crystal pair, criterion corrected after an initial miss — and does not
establish sensitivity to hydrophobic contacts, energies or any other discriminating interaction. The
unmeasured ranking "strongest negative in the record" is withdrawn.

## C12 · `selcal-deepternary-frame.json` — no external refutation follows

**Unchanged in the artifact:** a single `selcal_smarca2` preparation record, native `9DTY`, degrader
component `A1BB4`, **64** degrader atoms, superposition and readability fields.

**Superseded interpretation:** that shipped ligand coordinates are identical to the native structure over
**66** atoms, and that this refutes an external publication's *unbound* protocol claim from its own released
data.

**Correct reading, 2026-09-08:** the record is a preparation and readability record for one system, **not**
the asserted 66-atom equality on a released benchmark case. ⛔ **The external refutation is withdrawn.**
What survives is a finding about this program's own assumed input protocol and the consequent relabelling,
plus the in-set positive control at its memorisation-permitting scope.

**Reopening condition:** the exact already-retained released-case coordinate comparison, with pinned file
identities, and the primary text's statement of what the method withholds. ⛔ No new source retrieval is
authorised by this note.

---

## What this file does not do

- ⛔ It does not modify any artifact it names. Every original byte stands.
- ⛔ It does not retract a measurement. Every quantity above survives at the scope stated.
- ⛔ It does not authorise new computation, source retrieval, or reopening of any blocked program.
- ⚠ It does not settle the current summaries in `research/manuscripts/nr4a3-program-map.md` or
  `systems/graph/publications.json`. Those are shared files; exact patches are filed at
  `research/autonomy/opus-capacity-campaign-20260908/paper-lane/MF1-repair/patches/CURRENT-SUMMARY-PATCHES.md`
  for the integrator to apply.
