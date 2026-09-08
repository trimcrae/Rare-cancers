---
id: DOC-MF1-F01-F12-RESPONSE-MATRIX
title: "MF1 repair — the F01–F12 response matrix"
level: L4
kind: memo
status: live
canonical_for: []
purpose: Record, finding by finding, what the 2026-09-08 MF1 correction batch changed, where, and which stronger claims were withdrawn for want of retained evidence.
scope: The twelve findings of the independent final scientific review of the MF1 methods-record manuscript and the root adjudication that accepted them. It is a preparation record, not final-review closure.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---
# MF1 repair — the F01–F12 response matrix

**2026-09-08.** Response to the independent final scientific review of the frozen MF1 manuscript
(`FINAL-SCIENTIFIC-REVIEW-MF1.md`, SHA-256 `f4a0aceec8fdea6a1da62de2dc36ef88637c6288c05f1cc7fc318b3c971b32be`)
and to the root adjudication that accepted F01–F12
(`MF1-final-review-root-adjudication-20260908.md`, SHA-256 `071fcfc9…`, parent-verified).

- **Reviewed freeze:** `0b965a1279c81c10d9edc054842a33446e87762e`; main SHA-256
  `a9058b6c40e32549f878347b2d4f8c0ed3f8593320ce417ef29367179a7d0fe2`, 46,172 bytes. Verified byte-identical
  in the working tree before any edit.
- **Owned and edited:** `research/manuscripts/methods-record/degrader-methods-failure-record.md` (main, in
  place) and `research/manuscripts/methods-record/degrader-methods-failure-record-SI.md` (new supplement,
  generated).
- **Not edited, patches filed instead:** `research/manuscripts/nr4a3-program-map.md`,
  `systems/graph/publications.json`. See `patches/`.
- ⛔ **No original raw execution output, result file or protocol history was modified.** Every retained
  artifact this batch reads is unchanged; the extraction script reads and never writes them.
- ⛔ **No new science was produced.** No simulation, docking, co-fold, fetch, installation, `V4`, ablation
  sweep or re-analysis. `reviewer_calculations.py` was **not** rerun, and none of the reviewer's explicitly
  illustrative quantities (the t interval ≈ [−1.123, +0.863], the ratio 2.29) appears anywhere in the
  manuscript or supplement.

Legend: **ACCEPTED — CORRECTED** the claim is narrowed or restated; **ACCEPTED — WITHDRAWN** the claim is
removed; **ACCEPTED — ADDED** new material discharges the finding.

---

## F01 · The "adequately-powered null" is only a test whose p can reach alpha

**ACCEPTED — CORRECTED.** *Where:* main §1 abstract, §4.1(a), §6 table row 2, §6.3, §6.4, §10.5 item 2;
SI §S1 row 1.

Retained and reported: recorded tier `NULL`, register control state `fails`, **6 versus 5** admitted model
means, **22** legs admitted, **0** rejected records, **0** technical failures in either arm, statistic
**+0.4373 Å**, **p = 0.746753** (mirror 0.255411), reference set **462**, attainable p floor **1/462 ≈
0.0021645**. Reported as an **executed calibration attempt that did not meet its registered directional
criterion**.

Removed: "adequately powered", "cannot see … at all", and the claim that the reference-set floor
establishes sensitivity. The floor is stated as a discreteness property of the reference set and
explicitly not power. No new power calculation was manufactured from the observed effect.

Also carried: the E1 observable has **no established quantitative link** to degradation selectivity; the
promised co-fold/crystal input validation **had not been implemented before the panel ran**, with the 12
scored co-folds recording low-quality target↔E3 placement; a technically clean MD leg does not establish a
physically correct input or an adequately sampled observable.

**PRT3789/ACBI2 identity:** corrected in the current scientific summary (§4.1a, §6.4) — the criterion text
names ACBI2 (Kofink *et al.* 2022) while the panel's own `reference` block establishes direction from
PRT3789, `doi:10.1158/0008-5472.can-25-1141`, not open access, so no magnitude is quoted anywhere.
⛔ `selcal-verdict.json` and `selcal_panel.py` are **unchanged**; the historical bytes stand.

**Reopening condition, unmet:** a retained, identifiable, genuinely prospective power specification in the
E1 estimand with effect-size and noise assumptions, plus input-validity evidence. Not present in the
retained record; the narrower claim is published instead.

---

## F02 · Two seeds and an SD are not an effect bound; a preregistered null is not validity

**ACCEPTED — CORRECTED.** *Where:* main §1, §4.1(b), §6 table row 4, §6.1, §8.1 item 3, §8.2 item 2, §10.5
item 3; SI §S1 row 2.

Reported: **S = −0.1297 kcal/mol** with **0.3264 kcal/mol** dispersion of recorded kind `replicate_sd`,
from **two seeds per arm**; an **exploratory conditional estimate compatible with zero at the observed
precision**, whose operational completion condition was met.

Withdrawn: the assertion that this returns a bound, proves a null, or shows an absent wedge; and the
"excluding ≳0.65 kcal/mol at 2σ" translation (a patch to the roadmap line that carries it is filed, since
that file is not owned here).

Explained rather than dismissed: the `system_identity_problems` particle-count flag — different water
counts do not by themselves prove invalid physics and cross-species systems need not match, but the
calculation may not be treated as an unqualified bound while the flag is open. Qualified: the causal claim
is an intervention on the **modelled ligand Hamiltonian conditional on the chosen structures**, not a
biological causal test; the first-order opening-penalty cancellation holds only under a common reference
state and ensemble and is recorded as an argument.

⛔ The reviewer's illustrative t interval is **not** used as a replacement empirical result.

---

## F03 · Cycle closure does not localise the failure or exclude sampling error

**ACCEPTED — CORRECTED.** *Where:* main §4.1(c), §6 table row 1, §8.2 item 3, §10.5 item 1; SI §S1 row 3.

Retained: the **repeated wrong-sign operational calibration failure**, 3 replicates, absolute error 1.543
kcal/mol; R_ternary = −0.0312, R_binary = −0.2440, R = +0.2128 kcal/mol with `NONE QUOTED AT n=1`.

Removed: unique localisation to endpoint-state error, exclusion of sampling error, and "more sampling will
not fix it". Added: the residual is one linear contrast of six edge errors (errors 1, 2, 3 close exactly);
the closure artifact itself states endpoint-state errors are invisible to closure; the propagation record's
own power ≈ 0.63 at its measured upper noise bound is not a clean exclusion; a three-replicate "upper
bound" on sigma is not a confidence bound on the variance. Also corrected: "converged sampling … all
present" — the retained diagnostic account reports binary-arm ligand departure and a `MEASURED_FAILURE`
convergence state, so selected diagnostics are reported as selected diagnostics.

A roadmap patch is filed for the current summary that carries the reversed implication.

---

## F04 · The "largest retraction" merged different input sets and overstated persistence

**ACCEPTED — CORRECTED.** *Where:* main §9.1–§9.4, §1 abstract; also §8.1 item 1.

Separated into four incidents, each with the panel it actually affected: **contaminated descriptive-v3 and
shakeout co-folds** (2026-07-11 builds carrying 14-3-3ε for Elongin B) — ⛔ **the completed covalent panel's
2026-07-22 inputs are clean of that contamination**, correcting the earlier draft's opposite claim;
**wrong-interface post-processing** on the completed panel (positional chain split selecting Elongin C);
the **nm/Å unit error** and chain-blind reactive-cysteine search in the same class; and the
**wrongly simulated physical system** of the two `warhead_only` legs, which tethered the electrophile to an
Elongin C cysteine 12.4 Å away.

Corrected: the source says **existing tests missed** these defects, not that known-answer tests cannot
catch them — its own fixes are such tests. Persisted trajectories would have permitted rescoring of the
interface readouts; they could **not** repair the wrongly simulated legs. Persistence is specified as
inputs, identities, code and parameter versions *and* trajectories appropriate to the observable.

Census scoped to the **actually surveyed prefixes** `nrv04-covalent-results/` and
`nrv04-covalent-results-chainfix/`: 17 per-leg readout records, **0** multi-frame coordinate objects —
stated as a retrospective conclusion about those prefixes, not a proof about every external copy. The word
**"largest" is removed** (no magnitude measure is defined).

---

## F05 · A route-selected register is not complete ascertainment; the categories mixed axes

**ACCEPTED — CORRECTED and ADDED.** *Where:* main §1, §3 (audit methods and ascertainment), §5.1, §10.3;
SI §S2 (the complete 22-entry inventory) and §S3.

Preserved: the **20-instrument route partition, 4 `support` / 16 `disclosed_failing`**, against the
**22-entry numbered census**, with the inclusion rule stated and **`V2` and `V18`** named as census entries
outside the partition. The two counts are never summed. `disclosed_failing` is labelled an
**administrative route label, not a scientific failure total**.

Withdrawn: "the audit is complete, not selective" and "answerable by construction". Replaced by an explicit
ascertainment limit — a graph-generated view proves consistency with the graph, not discovery of every
method used; the census was added retrospectively and records that `V21` was quoted for months without a
row.

Added: the supplementary per-instrument inventory with **four separated axes** — control type/availability,
execution/eligibility, inferential outcome, claim scope — for all 22 entries. The main's §5.1 table now
distinguishes did-not-recover, ran-and-did-not-resolve, nondetection under an operational criterion, failed
mechanism hypothesis / negative control, no control exists, and never run. `V13` is a mechanism hypothesis;
`V15`'s permutation nulls are a negative control, not a positive benchmark; `V19` carries one executed arm
and one unrun decisive arm; `V22`'s "no control exists" is replaced by an **attempted panel with zero
gradeable cases**.

**Reopening condition, unmet:** a fixed audit universe with ascertainment evidence against the program's
executed and claimed methods. No whole-program failure rate is reported.

---

## F06 · "Every method … first" is contradicted; three attempts are not independent validations

**ACCEPTED — CORRECTED.** *Where:* main §1, §3 (retrospective/prospective), §6.2, §9.6, §10.5 item 6.

Withdrawn: "every method used to support a paralogue-selectivity statement was first put to a test whose
answer was already known", and "three independent, preregistered attempts". Replaced by **three recorded
attempts assembled retrospectively**, with the shared dependencies named: two are `V11` applications
sharing an E1 readout and the same permutation scorer; the third shares the program's structural inputs,
co-folding route, selection decisions and code base. Different instruments alone do not establish
statistical or failure-mode independence.

Chronology reported honestly: explicit pre-run freeze assertions exist and the consequence sentence was
written before the deciding run, but current freeze booleans and a version-control pin do not establish
which rule existed before outcome access; one preregistration file carries a backfilled 2026-08-05 date
against a 2026-08-02 outcome timestamp. Stated as a **gap in demonstrability, explicitly not evidence of
post hoc registration**. Wording replaced by *the retained protocol describes these rules as prespecified*.
⛔ No new chronology audit was run.

---

## F07 · Decoy calls and a pocket score do not prove universal impossibility

**ACCEPTED — CORRECTED and WITHDRAWN.** *Where:* main §4.1(d), §7.3, §8.1 item 2, §10.6; SI §S1 rows 4–5.

**22 of 38** is reported as a **positive-call rate among the selected decoys under this scoring
configuration**, explicitly not a measured biological false-positive rate (the archive supplies computed
scores and computational labels, not measured NR4A negative labels; the calibration module states the
distribution depends on receptor frames and the same background is used elsewhere to identify an
above-background candidate).

**0.259 versus D\* 0.53** is reported as the failure of **one operational screening gate on one receptor
frame** — not a statement about binding, ligand-induced states, or every molecule generated there.

Removed: "exclude a design class on evidence"; "a signal smaller than its own noise is not recoverable by
any downstream method"; "a candidate cannot be better than the pocket it was designed into" as a universal
rule; and the "within-repo false-positive rate" phrasing. The no-efficacy / no-selectivity safeguards are
kept and extended (§10.6 now also refuses design-class impossibility and downstream-impossibility claims).

---

## F08 · The V1 null concerns a defined polar-contact descriptor

**ACCEPTED — CORRECTED.** *Where:* main §5.2 (`V1` row), §7.5; SI §S1 row 6.

Reported: **zero qualifying sequence-variable heavy-atom polar contacts under this descriptor in the 16
generated NR4A3 models**, with the descriptor and threshold named (N/O heavy-atom pair within 3.5 Å on a
side-chain polar atom, at an aligned position where the residue differs) and identified as a
**proxy, not a measured hydrogen bond**. The known-answer recovery is identified as a **narrow in-sample
development/harness check** — one contact, one crystal pair, criterion corrected after an initial miss.

Removed: the unmeasured ranking "the strongest single negative in the record" and "a null with a working
detector behind it" as a sensitivity claim. Retained: these models provide no contact-based justification,
under this descriptor, for a selectivity claim.

---

## F09 · Two interpretations contradicted by the paper's own dependencies

**ACCEPTED — CORRECTED.** *Where:* main §7.2 (pose), §8.3 (genetics); SI §S1 row 7.

**F09a, pose.** Corrected to **6 systems, 5 gradeable: 4 same-cavity and 1 different-cavity**, with the
sixth ungradeable and excluded from the denominator rather than scored as agreement; the two sub-pockets
are 9.853 Å apart and both inside the shared search sphere; the cavity call is receptor-conformer
dependent, so neither an orientation-only nor a location-only reading holds. Retained: neither method is
thereby proven right or wrong. D3's 0/12 dispositions are unchanged (see F12).

**F09b, genetics.** Corrected to the asymmetric named evidence: **NR4A1** is the hard constraint (combined
`Nr4a1`/`Nr4a3` loss, postnatal lethality, PMID 17515897, corroborated PMID 29343483); **NR4A2** is
**bounded**, not unbounded (complete germline loss, neonatal lethality with complete penetrance, PMID
9092472 and PMID 9608532). "Would reconstitute a knockout genotype" is replaced by a qualified concern
about combined loss; ⛔ no pharmacological-knockout equivalence is claimed, and the
developmental/complete/lifelong versus adult/transient/incomplete caveat travels with both.

---

## F10 · The SD/MBAR-SE lesson compares different estimands

**ACCEPTED — CORRECTED.** *Where:* main §4.1(c) and §8.2 item 3 (the old §8 item 2 "understates it by
exactly that factor" is removed); SI §S1 row 3.

Retained: the warning that within-run precision does not describe between-run variability or accuracy, with
the observed quantities and their estimands and sample counts — **cycle replicate SD 0.375 kcal/mol at
n = 3** against **per-leg MBAR SE 0.097–0.132 kcal/mol** — and the statement that a cycle is a difference
of legs, so the two answer different questions and their ratio is not a transferable correction factor.

Removed: the exact inflation-factor claim. ⛔ The reviewer's illustrative 2.29 is **not** substituted, and
the record's own 3.28 is not quoted as a universal factor.

---

## F11 · The external unbound-benchmark refutation is not demonstrated

**ACCEPTED — WITHDRAWN.** *Where:* main §8.1 (item removed with a pointer), §9.5, §10.6.

The retained pointer `selcal-deepternary-frame.json` is a **single SMARCA2 preparation record with 64
degrader atoms**, recording superposition, snapping and file readability — not the asserted 66-atom
equality on a released benchmark case. The exact already-retained released-case coordinate comparison and
the primary protocol statement do **not** exist in the retained record.

⛔ **The external refutation is withdrawn.** What survives is a finding about this program's own assumed
input protocol and the consequent relabelling, plus the in-set positive control at its
memorisation-permitting scope. Reopening condition recorded in §9.5. ⛔ No new source retrieval and no
investigation of blocked programs was performed. A patch to the roadmap row that carries the 66-atom
assertion is filed.

---

## F12 · The main was not a standalone, reproducibly interpretable audit

**ACCEPTED — ADDED and CORRECTED.** *Where:* main §3 (audit methods), §4 (the quantitative record), §10.3,
§10.5, §11 (provenance, versioned locators, class distinctions, primary references), §12 (data and code
availability); SI §S1–§S3; `MF1-dependency-manifest.json`.

Added: a compact quantitative results table and a per-instrument supplementary inventory, both **generated
from the chosen frozen sources**, exposing control/reference identity, operational criterion, units,
eligible/excluded/failed/unrun counts, sampling unit, estimate and uncertainty type, actual result,
interpretive limit and source path. An audit-methods section states the universe, ascertainment,
retrospective/prospective status and the rule for contradictory or superseded records (follow the primary
artifact; record the disagreement). §11 distinguishes original raw execution outputs, retained reductions,
narrative annotations and new author extraction, and gives versioned locators with a SHA-256 and blob-id
manifest.

Corrected: the "0 tables" premise (the frozen main already carried four Markdown tables; ⛔ no decorative
figures are added); the residual field-frequency/novelty premise, removed from §1 and §10.2 and refused
in §10.6; and the data-availability statement, which now says explicitly that **no immutable public archive
or release has been created or verified and none is claimed accessible**. Input and trajectory gaps are
stated at the claims they limit (§9.4, §12) rather than as a global invalidation.

---

## Cross-cutting binding 12 — records preserved verbatim

- **D3, zero of twelve gradeable**, split preserved as **2 R2b exclusions / 6 `dock.prm` UNRUN / 1 fetch
  refusal / 3 alignment refusals**, with the unreadable-`dock.prm` cause attributed to the six and to no
  others (main §7.2).
- **Six actual cross-method pose comparisons executed** — so "the method never ran" is false (main §7.2).
- **D4, the executed calibration that failed** — retained as an executed, unsuccessful attempt under the
  registered operational rule, not an absent control and not an absent result (main §6.3).
- **`V4` unrun and unauthorised** — built and staged with no result key, never completed, not authorised
  (main §5.1, §6.2, §10.5 item 8).
- **`V21` 7 of 10**, `panel_readable: false`, blocking targets `CYP3A4`, `PXR`, `PPARG`, uniform repair did
  not restore readability (main §7.1).

---

## Unresolved limits carried forward

Listed in main §10.5 and repeated here: the cause of the wrong-sign calibration failure; the absence of any
established E1 effect size; the absence of a calibrator for `S`; the unrecoverable corrected-interface
readouts and the unrepairable wrongly-tethered legs; whole-program ascertainment; the demonstrability of
the prespecification chronology; the withdrawn external assessment; and the ungraded selectivity
free-energy axis (`V4`).

⚠ **These preparation claims are not final-review closure.** Root's focused verification of the changed
claims and their dependencies is the next step; this document is the map for it.
