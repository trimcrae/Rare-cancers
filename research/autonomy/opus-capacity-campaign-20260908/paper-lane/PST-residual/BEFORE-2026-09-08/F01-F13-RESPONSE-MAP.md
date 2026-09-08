# P-ST correction batch — response map for findings F01 to F13

Source of the findings: `FINAL-SCIENTIFIC-REVIEW-P-ST.md`, the complete 53,772-byte report
(sha256 `6dd9fd532e853d3ac5b1d8605dad79d585bdd1356598cc407eef8415adc4cf1a`), read in full together with
the complete 10,718-byte root memo `P-ST-final-review-root-adjudication-20260908.md`
(sha256 `e6240554…`, parent-verified), plus the reviewer's calculation source, results, stdout and exit
record, the source-extraction records and the collection records, all from the verified capsule.

Frozen inputs corrected: main `emc-surface-target-landscape.md` (99,615 B, sha256 `8931895d…0584df6f`)
and SI `emc-surface-target-landscape-si.md` (41,853 B, sha256 `92a7c49f…65cdafd1`) — the exact bytes the
reviewer read.

Legend: **APPLIED** = the correction is in the revised text. **SPECIFIED** = a byte-exact repair is
prepared but deliberately not applied here (no write authority outside this lane). **NOT DONE** = the
review's stronger route, which this batch does not attempt.

---

## F01 — the normal-tissue prior · P1 · APPLIED

- Renamed throughout as a **custom category heuristic** whose verdicts are stored historical labels, not
  Human Protein Atlas tiers and not a filter this study validated (Methods; SI S3; Table 1 caption;
  Table S2 caption; scope box; front matter).
- States the exact missingness measured in the artifact: quantitative tissue-specific and blood-specific
  nTPM null for **all 45 classified records**; the vital-tissue branch converts the missing value to an
  empty string and so never inspects an expression level; **all nine** liability labels come from the
  blood-category branch.
- States that the RESTRICTED rule's "restricted distribution" conjunct is not enforced —
  ALCAM, B4GALNT1 and GPC3 carry "Detected in many" and are still labelled RESTRICTED.
- "No vital-tissue signal", "clean window" and "a successfully checked normal-tissue filter" removed as
  conclusions everywhere in live prose.
- DLL3 is described as the **stored-label intersection only**, over the records that carry such labels;
  the six flagged antigens with no record (ALK, ENPP1, FGFR4, PDGFRA, SLC34A2, STEAP1) are named.
- CD3E control description corrected: it is tissue-**enriched** and reaches the immune branch, so it does
  not exercise the tissue-enhanced branch; the weak-immune-enhancement exemption is disclosed as tuning.
- ⛔ No HPA query, no imputation of a missing value, no reinterpretation of unavailable quantities.

## F02 — comparison design and transfer · P1 · APPLIED

- Title, front matter, abstract, Results, Discussion and Conclusion reset to a **retrospective,
  descriptive cross-context comparison**. "An estimate of how far a lineage-surrogate surface ranking
  transfers" is removed; the text states explicitly that no transfer-accuracy or ranking estimand was
  defined or evaluated.
- The **10 / 3 / 5** eligibility split is reported beside the **0 of 10** upward result; CD248, GPC2 and
  ROR1 are named as the one-platform three (ROR1 was previously omitted from that list in prose).
  FGFR1 and PTK7 are reported as meeting the downward rule on both.
- "Concordant" is defined as an **operational two-platform rule**; "not reproduced" is explicitly not
  used as a synonym for measured biological failure; equivalence, absence and therapy-route rejection
  removed.
- The claim that the comparator limitation "is no longer" binding is withdrawn: the Limitations now say
  the comparator basis remains central and the tissue cohorts bring their own comparator arms.
- The rare-tumour caution is downgraded to a methodological consideration.

## F03 — sequencing scale · P1 · APPLIED (prose) + SPECIFIED (annotation)

- Methods, SI S4, Table 4 caption, Table 5 caption, Table S6 caption and every sequencing sentence now
  identify the deposit's depth/sample-mean normalisation followed by **square-root compression**, quoted
  verbatim from the retained GEO series record, and call the values and ratios **deposited compressed
  summary scores**, never read densities, fold changes or "times expression".
- The actual reduction order — median across libraries per peak, then median across a gene's peaks — is
  stated in Methods and SI S4, with the note that the orders do not commute and that squaring an
  aggregate ratio does not recover a linear fold.
- **Every numeric value is unchanged.**
- The misleading `_contrast` aggregation annotation is corrected by a separate, additive,
  original-preserving repair specified byte-exactly in
  `annotation-correction/ANNOTATION-CORRECTION-gse28866-aggregation-order.md`. It is **not applied** by
  this lane and no producer was re-run.

## F04 — normal and comparator panel design · P1 · APPLIED

- **17 adult and 10 fetal** normal libraries with the exact organ weighting (5 breast, 9 lung, 1 uterus,
  3 colon, 3 bowel, 6 kidney) stated in Methods, SI S4, SI Note S5, Table 2 and the Table 4/5 column
  headers.
- **32 non-EMC sarcoma libraries from 30 specimens**, with the deposit's two named technical duplicates,
  stated as a weighting issue and not an inflated sample size.
- Pooled-normal medians are described as descriptive for that mixture; they do not establish adult
  normal exposure or safety anywhere.
- The asserted ALCAM "the two instruments point different ways" / failed-normal-window adjudication is
  **withdrawn** in the main text and SI Table S2 note: a categorical restriction label and a
  tumour-to-pooled-normal ratio are different quantities, and the true fact that the two sources carry
  different information is preserved.

## F05 — uncertainty · P1 · APPLIED

- "(ns)" redefined everywhere as *q* >= 0.05, never as an interval containing zero; intervals are labelled
  **ordinary pointwise 95 %** intervals and stated to be un-adjusted for multiplicity.
- The counterexamples are stated: **14 GPL6244 and 8 GPL3290** non-significant rows have intervals
  excluding zero, with KIT (0.2433 to 2.4633, *q* = 0.076) and MCAM (−0.5346 to −0.0413, *q* = 0.080)
  named; CDH11's GPL6244 row is corrected in prose for the same reason.
- **Half-width** used consistently; the factor-of-two error is corrected (0.259 and 0.957 are median
  half-widths; full widths about 0.5173 and 1.90495). SI S7's "the elevation a gene's own data cannot
  exclude" is explicitly corrected.
- The stored **upper-middle median convention** (0.9571) is described accurately beside the conventional
  median half-width (0.952475).
- "Exact *p*" replaced by Welch two-sided *p* on Welch-Satterthwaite approximate degrees of freedom, with
  the statement that it is not an exact distribution-free calibration.
- Stated that neither a median half-width nor the smallest significant effect is a power or equivalence
  analysis. ⛔ No new statistics were run.

## F06 — controls and chronology · P1 · APPLIED

- Biological reference genes, reader regression checks, classifier development checks and genuine
  external validation are separated in Methods, Results, SI S2, SI S3 and Table S4.
- ENO3's expectation is disclosed as resting on ENO3 having already been measured up in the **same two
  series**; its cited transactivation result is identified as **TFG::NR4A3**.
- MKI67-flat is stated to be a motivated expectation and **not a known answer**; its GPL3290 reading is
  reported as not passing an ordinary two-sided 0.05 Welch test, and the old |*t*| >= 2 "not flat" label
  is identified as a readability label rather than the declared test.
- "Prespecified" removed for the three sensitivity analyses (main and SI) and replaced with recorded and
  conducted, with the explicit note that no dated pre-outcome specification was identified. The same
  change is made for the two scan self-checks.
- Blanket "a working control licenses reading the other rows" removed in both documents; the four
  sequencing negatives are relabelled biologically motivated reference antigens.

## F07 — denominators and missing states · P1 · APPLIED

- The abstract's "76 lines" is corrected: 76 is class membership, **45** expression-bearing lines carry
  the tested actionable rows.
- The successive denominators are stated and kept apart in SI S1: **2,826 / 2,692 / 47 / 18** and the
  classic **18 / 15 / 9**.
- The distinct missing-evidence states are enumerated in the main Limitations and SI Note S5: no
  normal-tissue record; no retained selectivity result; no board row; a contrast excluded for
  insufficient comparator observations (NR4A3 on GPL3290); a measured non-significant contrast; and a
  significant decrease.
- "Never evaluated" replaced by **"no retained selectivity result"** for CSPG4, B4GALNT1 and SSTR2 in the
  Results, Discussion, Table 1 rows, Table 1 caption and SI Note S1 L4, with the explicit statement that
  absence from retained selected output is not proof a gene was never evaluated. M 499's "no per-gene row
  in any committed artifact" is narrowed to the retained selectivity rows.
- Cohort arithmetic corrected: 42 − 6 − 29 = **7** remaining arrays, not 13.
- Residual **fibrosarcoma → myxofibrosarcoma** corrected at the FAP discussion and at SI Note S5, with
  the deposit's verbatim GSM600957–GSM600962 annotations cited in Methods.

## F08 — stale Figure 1 · P1 · APPLIED, by omission

- **The figure is omitted from the outgoing candidate and not replaced.** The display item is deleted,
  the in-text call is removed, and a short paragraph in its place records exactly why: five current
  Table 1 rows omitted (ALCAM, CD248, CSPG4, ERBB2, LRRC15); "clean window", "target-worthy" and a
  "NOT EVALUATED" band printed inside the image; and a quadrant boundary drawn on a positive selectivity
  effect rather than the *q*-based decision.
- The original PNG (1610 × 896, sha256 `130042b6…c439bd`) and `emc_surface_figure.py` are retained
  **unaltered** and are carried in the packet manifest as historical bytes; the renderer is listed for
  provenance only, with the note that it reads a mutable remote cache so re-running it would not
  reproduce the retained image.
- ⛔ No renderer was run, nothing was redrawn, no new graphic producer and no fresh measurement.
- Checked mechanically: the original PNG's sha256 is unchanged, no `**Figure 1.**` display item remains,
  no in-text call remains, and the three printed assertions appear in live prose only inside the
  paragraph that records the omission.

## F09 — biological interpretation · P1 · APPLIED

- Array percentiles are described as **ranks across probes**, never as calibrated detection limits or
  evidence of saturation: PRAME's "floor of every readable cohort" and VCAN's "the background is
  saturated" are both rewritten, and the claim that a high rank makes a significant contrast
  non-discriminating is removed.
- Compartment claims become hypotheses: absent stroma is consistent with the LRRC15 reading but is not
  shown to have caused it, and SI Note S1 L5 now records FAP's 16 % expressed / 56 % detectable fractions
  and that LRRC15's 0.0 expressed fraction means no line passed the threshold, not literal absence.
- BGN and VCAN carry matrix annotations; CD44 is no longer collapsed into "all three are secreted
  matrix", and bulk transcript data are stated not to establish which cells deposited a compartment.
- "A single measurement discriminates the four explanations" corrected in main Results, main Conclusion
  and SI Note S4: a spatial or single-cell dataset bears on the compartment explanation only.

## F10 — multiple testing and panels · P2 · APPLIED

- The two per-platform Benjamini-Hochberg families are retained and described as internally consistent;
  their intersection is labelled an **operational concordance**, with the explicit statement that
  **joint replicability FDR was not estimated** (main Limitations, Table 5 caption, SI Table S7 note,
  SI Note S5).
- The **17 available panel tests** are labelled exploratory and unadjusted in Table S5's caption and in
  the main Results, with differing membership and coverage between platforms disclosed.
- Functional conclusions removed: no defective class-I presentation, no peptide-HLA route failure, and
  the route-panel disagreement is no longer called "partly a coverage artefact" — the membership
  difference is stated as a reason the scores are not comparable, with the note that no matched-member
  comparison was run.

## F11 — reproducibility · P1 · APPLIED

- Data availability now names the actual statistics generator `emc_tissue_read_statistics.py`, its two
  inputs and its `accession-symbol-cache.json` helper dependency, and adds
  `gse28866_tumour_vs_normal.py` and the full-text screen artifact.
- The per-sample claim for the sequencing artifact is corrected: it stores **group-level peak summaries**.
- A new "What can and cannot be reproduced" paragraph separates offline recalculation from
  original-source reproduction, naming the three gaps: the scan's complete universe / per-line
  observations / *p*-value family; an audited probe-annotation chain; and the original peak table.
- A versioned, hash-manifested **local** packet is delivered (`packet/PACKET-MANIFEST.json`, 25 entries,
  every hash measured in this lane). The text states that **no public immutable locator exists and none
  is claimed**. ⛔ No missing original was acquired.
- Original execution artifacts are preserved and kept separate from the later annotation correction,
  which is specified but not applied.

## F12 — novelty and sources · P2 · APPLIED

- The prior-art passages are bounded to what the retrieval and screening methods can support: the
  corpus is **237 retained text files plus an index** (not 238 full texts), the full-text pass is
  described as a narrower algorithmic rule nested under a general term condition over a limited antigen
  list, and no field-wide first, absence or frequency claim is made. The "disease absent from public
  data" premise is labelled a programme assumption.
- Originating deposits are credited, with the retained esummary's links stated as links only:
  **GSE24369 → PMID 21536545, GSE28866 → PMID 22929540, GSE4303 → PMID 15920699**. No bibliographic or
  full-text detail is asserted for the two new links, and they are placed in Methods and Data
  availability rather than fabricated into the numbered reference list.
- Clinical and mechanism claims without retained supporting text are removed: the lorvotuzumab
  "discontinued" claim and the "adult sarcoma has a poor record for cell products and engagers" claim.
- The unavailable B4 PNAS supplement scope stays closed; nothing was retried.

## F13 — identity correction · P2 · APPLIED

- The withdrawal of H-EMC-SS as authenticated EMC evidence is retained unchanged.
- "Three independent readouts" → **three information sources**, with the statement that their error
  mechanisms are related and none was independently validated.
- "The model being in the file is what makes this a reading of absence" is corrected: presence
  establishes that the model was represented and that this filtered caller reported **no qualifying
  call**; read coverage, caller sensitivity, filtering and transcript structure remain relevant, and the
  Cellosaurus caution concerns an *EWSR1* fusion while EMC has other recorded NR4A3 partners.
- The existing Appendix A1 qualification that dropping the line bounds stored mean effects and does not
  rederive the rank-test or BH decisions is preserved as it stood.
- ⛔ Authentication and sequencing were not reopened.

---

## What this batch deliberately did NOT do

The review's Section 5 reopening conditions are **NOT DONE** and remain unavailable: tissue-complete
normal source and an independent classifier validation; a defined comparable transfer task; an analysis
on the original sequencing scale with an adequate normal-panel design; original-source provenance
sufficient to claim reproduction; original pre-outcome or external calibration evidence; and direct
evidence for any asserted mechanism, protein or function. No source acquisition, producer run, raw
reanalysis, new baseline review, closed-route retry, B4 retry or publication step was performed.
