#!/usr/bin/env python3
"""P-ST correction batch, part 2: residual scale wording, the SI figure line, and the
Appendix A7 correction register for this batch. Same contract as part 1: every edit must
match exactly once. Runs on the part-1 output, in place.

Usage: python3 apply_pst_correction_part2.py <revised_dir>
"""
import hashlib
import pathlib
import sys

MAIN = "emc-surface-target-landscape.md"
SI = "emc-surface-target-landscape-si.md"

APPENDIX_A7 = """
### Appendix A7 — Final-review correction batch (2026-09-08): findings F01 to F13

This batch applies one independent final scientific review of the frozen candidate
`9f571e8170fb81dbe4d78515981ccb57c7a78b3e` (report `FINAL-SCIENTIFIC-REVIEW-P-ST.md`, 53,772 bytes,
SHA256 `6dd9fd532e853d3ac5b1d8605dad79d585bdd1356598cc407eef8415adc4cf1a`) and its root adjudication.
Every change is a correction of claim scope, measurement description or accounting against records that
already existed. **No producer was re-run, no figure was rendered, no source was fetched, no statistic
was recomputed and no artifact was edited by this batch.** Three arithmetic or labelling corrections
change printed values: 42 arrays minus 6 EMC minus 29 comparators is 7 remaining arrays and not 13; a
residual "fibrosarcoma" label becomes myxofibrosarcoma; and the prior-art corpus is 237 retained text
files plus an index rather than 238 full texts.

| Finding | Superseded position, retained here | What both documents now say |
|---|---|---|
| F01 | A Human Protein Atlas normal-tissue prior filtered the candidates, with "no vital-tissue signal" and a clean window; controls validated the classifier | The verdicts are stored labels of a custom category heuristic. The quantitative tissue-specific and blood-specific nTPM fields are null for all 45 classified records, so the vital-tissue branch never inspected an expression level and all nine liability labels come from the blood-category branch. ALCAM, B4GALNT1 and GPC3 carry RESTRICTED despite "Detected in many". DLL3 is a stored-label intersection only; six flagged antigens carry no record. The CD3E control reaches the immune branch and does not exercise the tissue-enhanced branch |
| F02 | The contribution is an estimate of how far a lineage-surrogate ranking transfers; the priorities were "not reproduced" in EMC tissue | The surrogate contrast and the tissue contrasts are different estimands in different compartments; no transfer-accuracy or ranking estimand was defined or evaluated. Reported instead: the 10/3/5 two-platform eligibility split, zero of ten meeting the upward rule, FGFR1 and PTK7 meeting the downward rule, with signed estimates retained. The surrogate-caution for other rare-tumour studies is a methodological consideration, not a demonstrated prescription |
| F03 | Sequencing values were read densities and their ratios "times" expression | The deposit normalises by sequencing depth and sample mean and then takes the square root of each value; every sequencing value and ratio here is a deposited square-root-compressed summary score. The reduction is the median across libraries per peak, then the median across a gene's peaks. Numeric values are unchanged; squaring a ratio would not recover a linear fold. The contradictory aggregation annotation in the source-level documentation is corrected separately and is not applied to any original output |
| F04 | The 27 normal libraries were a normal-organ panel supporting an on-target off-tumour exposure axis; the two normal-tissue instruments "point different ways" for ALCAM | The normal arm is 17 adult and 10 fetal libraries with unequal organ weighting, and the 32 non-EMC sarcoma libraries come from 30 specimens with two technical duplicates. Pooled medians are descriptive for that mixture and bound nothing about adult exposure. A categorical restriction label and a tumour-to-pooled-normal ratio are different quantities, so the asserted validation disagreement is withdrawn |
| F05 | "(ns)" meant an interval containing zero after correction; "exact *p*"; the median 95 % interval was 0.259 and 0.957 | "(ns)" means *q* >= 0.05; intervals are ordinary pointwise 95 % intervals and are not multiplicity-adjusted, and 14 GPL6244 and 8 GPL3290 non-significant rows have intervals excluding zero. The *p* values are Welch two-sided values on Welch-Satterthwaite approximate degrees of freedom. 0.259 and 0.957 are median **half-widths** (full widths about 0.52 and 1.90); the stored 0.957 uses the upper middle of an even-length list against a conventional median half-width of 0.952475. Neither figure is a power or equivalence analysis |
| F06 | Three genes with known answers were read before any antigen, and a working control licensed reading the other rows; three prespecified sensitivity analyses | These are biological reference genes and reader regression checks, not independent known-answer calibration or external validation. ENO3's expectation rests on ENO3 having already been measured up in the same two series, and its cited transactivation result concerns TFG::NR4A3. MKI67-flat is a motivated expectation, not a known answer, and its GPL3290 |*t*| >= 2 label is not the declared two-sided test. No dated pre-outcome specification was identified, so the sensitivity analyses are described as recorded and conducted |
| F07 | The rank test ran across 76 lines; "never evaluated"; 13 of 18 with a tissue reading; "the remaining 13 arrays"; a residual fibrosarcoma label | 76 is class membership and 45 are the expression-bearing lines the tested rows use. The successive denominators 2,826 / 2,692 / 47 / 18 and the classic 18/15/9 are kept separate. Ten of the 18 carry both contrasts, three one, five none. "No retained selectivity result" replaces "never evaluated" for CSPG4, B4GALNT1 and SSTR2, and absence from retained selected output is not proof a gene was never evaluated. 42 − 6 − 29 = **7** remaining arrays. "Fibrosarcoma" becomes myxofibrosarcoma |
| F08 | Figure 1, a 13-gene prioritisation plot, with a caption describing it as drawn over Table 1 | **The figure is omitted from this version and not replaced.** It omitted five current Table 1 rows (ALCAM, CD248, CSPG4, ERBB2, LRRC15) and printed "clean window", "target-worthy" and a "NOT EVALUATED" band inside the image, none of which the retained evidence supports, and its quadrant boundary used a positive selectivity effect rather than the *q*-based decision. A caption-only patch could not repair assertions printed in pixels. The original PNG (`research/modalities/emc-surface-prioritization.png`, 1610 x 896, SHA256 `130042b6afab8aea28874d37dd684cde96886ab25b488ab65b83dac391c439bd`) and its renderer and provenance are retained unaltered as historical bytes; no renderer was run and nothing was redrawn |
| F09 | PRAME "at the floor of every readable cohort"; a saturated background for VCAN; stroma caused the LRRC15 reading; one measurement would discriminate the four explanations | Array percentiles are ranks across probes and not calibrated detection limits or evidence of saturation. Absent stroma is consistent with the LRRC15 reading but is not shown to have caused it, and FAP is detectable in 56 % of class lines. Compartment attributions are hypotheses. A spatial or single-cell measurement bears on the compartment explanation only; it does not resolve the comparator, culture or platform explanations |
| F10 | The three-gene intersection carried the correction's error rate; panel trends supported functional conclusions; the route-panel disagreement was partly a coverage artefact | The two per-platform Benjamini-Hochberg families are retained and internally consistent; their intersection is an operational concordance and **no joint replicability FDR was estimated**. The 17 available panel tests are exploratory and uncorrected, with differing membership and coverage between platforms. No class-I presentation failure, peptide-HLA route failure or demonstrated coverage artefact is asserted |
| F11 | "Every number is reproducible offline from the artifacts named"; per-sample sequencing values; a data statement that omitted the statistics generator | Data availability now names `emc_tissue_read_statistics.py` and its inputs and helper dependency, states that the sequencing artifact holds group-level summaries rather than per-sample values, and separates what can be recalculated offline from retained derived records from what cannot be reconstructed back to the original public source: the scan's complete universe, per-line observations and *p*-value family; an audited probe-annotation chain; and the original peak table. A local hash-manifested packet exists; **no public immutable locator exists or is claimed** |
| F12 | A prior-art screen establishing that nothing is indexed; 238 full texts; a discontinued CD56 programme and modality-class performance claims | The searches are bounded retrieval and screening outcomes and support no field-wide first, absence or frequency claim. The corpus is 237 retained text files plus an index. The originating deposits are credited, with the GEO summary record's links GSE24369 → PMID 21536545, GSE28866 → PMID 22929540 and GSE4303 → PMID 15920699 — links only, establishing no article's full text or metadata. The lorvotuzumab discontinuation claim and the modality-class performance claim are removed. The unavailable B4 PNAS supplement scope stays closed |
| F13 | Three independent readouts resolved the H-EMC-SS identity; presence in the filtered fusion file made the missing call "a reading of absence" | The withdrawal of H-EMC-SS as authenticated EMC evidence stands. They are three information sources with related error mechanisms, not independent confirmations. Presence in the filtered file establishes that the model was represented and that this filtered caller reported no qualifying call; it is not verified biological absence. Dropping the line bounds stored mean effects and does not rederive the rank-test or Benjamini-Hochberg decisions |

⚠ **Appendix A6 is itself partly superseded by this batch and is retained unaltered.** Its register
describes the sensitivity analyses as "prespecified" and the array *p* values as "exact"; F06 and F05
above replace both descriptions. Its substantive corrections — the three concordant genes, the 9/18
set definitions, the myxofibrosarcoma label and the CSPG4 scan-versus-prior distinction — stand.

⚠ **What this batch does not establish.** It does not validate the normal-tissue heuristic, define or
estimate a transfer task, recover the original sequencing scale, reproduce any analysis from its
original public source, establish prespecification, or estimate a joint replicability false-discovery
rate. Those claims remain unavailable on the evidence in hand, and the revised paper still requires
focused scientific verification and its applicable publication gates before any submission.
"""

EDITS_MAIN = [
 ("F03-methods-pooling",
  """nothing about normal-organ exposure. Read densities from 3'-end sequencing are not array intensities and
are never pooled with them.""",
  """nothing about normal-organ exposure. Deposited sequencing scores are not array intensities and are never
pooled with them."""),

 ("F03-limitations-pooling",
  """Several further constraints apply to every number above. Read densities from 3'-end sequencing are never
pooled with array intensities.""",
  """Several further constraints apply to every number above. Deposited sequencing summary scores are never
pooled with array intensities, and, being square-root-compressed deposit values, they are not linear
abundances and their ratios are not fold changes."""),

 ("A7-register",
  """---
*Provenance: consolidates the stage-1 surfaceome scan""",
  APPENDIX_A7 + """
---
*Provenance: consolidates the stage-1 surfaceome scan"""),
]

EDITS_SI = [
 ("SI-F03-S4-pooling",
  """*t* and degrees of freedom. Read densities and array z scores are never combined.""",
  """*t* and degrees of freedom. Deposited sequencing scores and array z scores are never combined."""),

 ("SI-F08-L4-figure",
  """because the artifact stores gene counts rather than the gene list. Its absence from the
selective-and-restricted intersection is therefore a coverage gap and not a rejection. The rendered
figures are produced from the same JSON, so a gene with no row has nothing to plot.""",
  """because the artifact stores gene counts rather than the gene list, and absence from the retained
selected output is not proof that the scan never evaluated it. Its absence from the
selective-and-restricted intersection is therefore a coverage gap and not a rejection. The prioritisation
figure was produced from the same JSON, so a gene with no row had nothing to plot; that figure is omitted
from the current version of the main text (Appendix A7) and its original bytes are retained unaltered."""),
]


def apply(text, edits, label):
    for eid, old, new in edits:
        n = text.count(old)
        if n != 1:
            raise SystemExit("FAIL %s/%s: matched %d times (expected 1)" % (label, eid, n))
        text = text.replace(old, new, 1)
        print("    %-30s %5d -> %5d chars" % (eid, len(old), len(new)))
    return text


def main():
    d = pathlib.Path(sys.argv[1])
    for name, edits in ((MAIN, EDITS_MAIN), (SI, EDITS_SI)):
        p = d / name
        raw = p.read_text(encoding="utf-8")
        print("%s: before %s (%d bytes)" % (name, hashlib.sha256(raw.encode()).hexdigest(), len(raw.encode())))
        new = apply(raw, edits, name)
        p.write_text(new, encoding="utf-8")
        print("%s: after  %s (%d bytes)" % (name, hashlib.sha256(new.encode()).hexdigest(), len(new.encode())))


if __name__ == "__main__":
    main()
