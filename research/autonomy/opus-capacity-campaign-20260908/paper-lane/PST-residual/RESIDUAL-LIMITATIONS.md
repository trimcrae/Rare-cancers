---
id: DOC-OPUS-CAMPAIGN-PST-RESIDUAL-LIMITATIONS
title: "What the narrowed P-ST comparison still cannot support"
level: L4
kind: limitations
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Residual limitations after R1 to R8, 2026-09-08

This batch removed claims. It added no measurement, no statistic, no source and no search, so nothing
here became more supported than it was before.

## 1. What the narrowed comparison still cannot support

* **No identified compartment.** Missing stromal coverage is a *compatible explanation* for the low
  LRRC15 reading. It is not separated from the alternatives by any measurement retained here. CD248 and
  PDGFRB culture expression does not resolve which compartment contributes their bulk-tumour signal, and
  no spatial or single-cell measurement was made or requested.
* **No validated normal-tissue window, no absolute abundance, no calibrated null.** The normal-tissue
  verdicts are stored labels of a custom category heuristic over records whose quantitative fields are
  null. Cross-probe ranks and square-root-compressed deposited scores cannot express an absolute
  receptor level. A zero pooled median over an unequally weighted adult and fetal panel is not absence
  in any contributing library or organ.
* **No transfer estimate and no generalised surrogate failure.** No transfer task or estimand was
  defined or evaluated.
* **No equivalence, power or bound.** A non-significant contrast is a measurement that did not meet the
  *q* decision. No equivalence test was performed, and a median half-width describes typical platform
  imprecision rather than any particular gene's interval.
* **No clinical prioritisation, therapeutic window, efficacy, safety or selectivity claim.** There is no
  wet lab. Nothing here measures protein, surface localisation, receptor density or epitope
  accessibility. A scan or a stain would observe uptake, or protein and its localisation, in the
  material sampled; neither would decide population expression or route suitability.
* **No reconstruction of the sequencing reduction.** The retained records hold final gene-level arm
  medians with peak and library counts. Retrieval and ratio/band arithmetic over those medians is
  available; the two-stage per-library / per-peak reduction that produced them is not, and the original
  peak table is not retained.
* **No complete scan universe.** The scan's per-line observations and full *p*-value family are absent.
  Whether CSPG4 was ever scanned is undecidable from the retained artifact; "no retained selectivity
  result" is the supported statement.
* **No field-wide history.** Priority, prior-absence and frequency statements are limited to the
  inspected bounded retrieval and to this programme's own chronology.
* **The two structural risks are unchanged.** Small archival cohorts on decade-old platforms with
  different comparator arms and a disclosed GPL3290 reference/RNA-input mismatch; and a comparison of two
  designs that were never built to be compared.

## 2. The four preserved historical limitations — verbatim, not reconstructed

These are records of executions this author did **not** run and did **not** reconstruct. They are
reported as they stand.

1. **The author's apply receipt is `EXIT=1`.** `…/P-ST-correction/execution/apply-exit.txt` contains
   `EXIT=1`, beside an `apply-stdout.txt` describing 66 main plus 30 SI edits and `TOTAL EDITS: 96` and
   an empty `apply-stderr.txt`. The non-zero exit is preserved as delivered. No successful exit is
   inferred and no omitted failure transcript is invented.
2. **The later 54-check run is `EXIT=0`.** `checks-stdout.txt` ends `54 passed, 0 failed` and
   `checks-exit.txt` contains `EXIT=0`, at HEAD `a6a21fc591d2451038cdf53449b91e3990d59cfb`. That is a
   limited successful author check **at its recorded inputs** — not scientific clearance, not proof that
   all F01–F13 claims were corrected, and not independent validation from original public sources.
3. **No standalone part-2 exit file was delivered.** The 19 delivered P-ST correction files include the
   part-2 stdout and an empty part-2 stderr, but **no part-2 exit file**. That gap is recorded, not
   filled: no exit code is inferred for it in either direction.
4. **The shorthand-command limitation.** `CORRECTION-RECORD-P-ST.md` lines 79–81 display an invocation
   using `research/autonomy/.../` shorthand; it is **not a literal runnable command**. Lines 103–106
   discuss initial failed anchors without exposing every initial failure message, and the "66"/"71"
   accounting at lines 43 and 103 describes main edits and part 2 without incorporating the 30 SI edits
   already listed in the first stdout.

## 3. The old hardcoded / string checks are LIMITED checks

`check_pst_correction.py` compares **hard-coded expectations** — a fixed *q* list at lines 58–74, six
fixed sequencing expectations at lines 103–112, and a few exact search strings at lines 172–197. It does
**not** extract each table's actual current cells, and its "present" checks can succeed when a correct
disclaimer appears anywhere while contradictory text survives elsewhere. Its 54/0 result is therefore
**not proof that all live prose or table cells agree**. The residuals R1–R8 exist precisely because that
limitation let contradictory passages through: for F07 it searched two phrases but not the surviving
"surrogate stage never evaluated", and for F09 it searched the old PRAME floor sentence but not the live
stromal-floor claim.

The same is true of this batch's own `check_pst_residual.py`. It is a direct text, package and
annotation integrity check over stored fields and exact strings. It confirms that specific withdrawn
wordings are gone from live prose and that specific corrected wordings are present. **It is not a
scientific verification of the paper and not a reproduction of any producer.**

## 4. The two failing checks after this batch, and why neither was made to pass

Re-running the retained checker gives **52 passed, 2 failed, exit 1** (`checks/RUN-08-pst-checker/`).
Both failures are correct and are left in place. Nothing was weakened.

* **`F11-sequencing-not-per-sample`** requires the literal string
  `"group-level peak summaries and not per-sample values"` in the main text. R4 required that exact
  phrasing to be replaced, because calling the records "group-level peak summaries" invites the
  misunderstanding that the per-peak reduction can be recalculated from them. The **artifact half** of
  the same check still holds and was re-verified independently: every `per_gene.values` record carries
  `n_peaks` and the three arm medians and carries no per-sample, per-library or per-peak field
  (`checks/RUN-11-residual-integrity`, `R4-artifact-holds-final-gene-medians`, exit 0). The check fails
  because its hard-coded string is now out of date, not because the claim is wrong — a direct
  illustration of section 3.
* **`packet-manifest-reproduces`** names exactly four CHANGED entries: the two files the parent's F03
  application changed, and the two manuscript paths R7 integration changed. `PACKET-MANIFEST.json` is a
  dated historical identity record and was deliberately not rewritten. See `CURRENT-PACKET.md` §5.

## 5. This author's own failed runs, preserved

`checks/RUN-01-panel-count-FAILED/` (exit 1, wrong assumption about the artifact's structure),
`checks/RUN-03-apply-FAILED/` (exit 1, a wrong path constant — the script wrote nothing), and
`checks/RUN-10-residual-integrity/` (exit 1, this author's own occurrence-count expectation was wrong;
the expectation was corrected to the measured truth and both runs are kept). No anchor, guard, matcher
or test was loosened in any of these fixes.

## 6. Scope of this batch

The candidate's disposition is not changed by this document. The batch delivers the narrower archival
comparison the adjudication admitted. It is not publication clearance, not a submission decision, and
not a lifting of any hold on the stronger claims.
