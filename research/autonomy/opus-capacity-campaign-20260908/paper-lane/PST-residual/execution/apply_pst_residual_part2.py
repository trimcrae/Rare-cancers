#!/usr/bin/env python3
"""P-ST residual batch R1-R8, part 2: the Appendix A8 residual register (main text).

Exact-match. Must match exactly once or exit non-zero without writing.
"""
import hashlib
import pathlib
import sys

MAIN = pathlib.Path(__file__).resolve().parents[2] / "P-ST-correction/revised/emc-surface-target-landscape.md"

ANCHOR = """⚠ **What this batch does not establish.** It does not validate the normal-tissue heuristic, define or"""

BLOCK = """### Appendix A8 — Focused-verification residual batch (2026-09-08): residuals R1 to R8

One focused verification of the F01-F13 batch held the returned candidate and set out eight residuals.
This register records what those residuals changed in the two documents. The superseded positions are
retained here verbatim; the corrected positions are what both documents now say. No new measurement,
statistic, search or source was made for this batch, and every previously reported value is unchanged.

| Residual | Superseded position, retained here | What both documents now say |
|---|---|---|
| R1 | The stromal floor was "demonstrated by LRRC15"; SI Note S1 L2 was headed "the stromal floor demonstrated" and said LRRC15 and FAP show what a stroma-only antigen looks like; CD248 and PDGFRB were exempted from the compartment caution because mesenchymal tumour cells transcribe them | LRRC15's expressed fraction of 0.0 means that no scanned line exceeded the chosen threshold: a threshold result, not a calibrated detector floor and not a demonstrated cause. FAP reads 0.16 expressed and 0.56 detectable, so it is not measured here as stroma-only. CD248 and PDGFRB culture expression shows there is something in the culture to measure and does not resolve which compartment contributes their bulk-tumour signal. Missing compartment coverage is one compatible explanation, not an identified cause. The line-authentication limitation is kept separate |
| R2 | A non-significant surrogate result "removes a transcriptomic rationale" and "the transcriptomic case"; a FAP-directed route "cannot claim EMC as a selectively FAP-rich indication"; SSTR2 showed "no striking absolute signal" and a scan or stain was "the cheap decisive measurement"; CSPG4 was "flat" on GPL3290 and "silent there"; a non-significant row was read through the median half-width; PRAME's zero pooled normal median was described as absence from normal organs | These particular contrasts provide no significant evidence of upward enrichment; no target-selection utility, equivalence bound or protein criterion licenses removing a transcriptomic case, and no route-level or indication decision follows. Cross-probe ranks and transformed summary scores cannot express an absolute receptor level. A scan or stain would observe uptake, or protein and its localisation, in the material sampled; neither decides population expression, a therapeutic window or route suitability. The GPL3290 CSPG4 estimate is a negative, imprecise, non-significant contrast (Δ = −0.189, 95 % CI −1.23 to +0.86, *q* = 0.764) and the stored "flat" label is a banding convention, not an equivalence result or a biological state. A median half-width describes typical platform imprecision and does not determine any particular gene's interval. A zero pooled median over an unequally weighted adult and fetal panel is not absence in any contributing library, organ, or in normal organs generally. Every estimate, *q* and recorded sensitivity analysis is preserved unchanged |
| R3 | The classic-antigen subset and the retained 47-antigen set were called nested, the latter containing the former; CSPG4 was "a gene the surrogate stage never evaluated" and "outside the stage-1 scan"; "the empty selective-and-restricted intersection" was unscoped; missing observations, a non-significant contrast and a significant decrease were grouped as none being a low or negative reading | The two sets **overlap in 15 antigens and neither contains the other**: CSPG4, B4GALNT1 and SSTR2 are classic antigens with no retained selectivity row. The nine-classic and 18-total selectivity flags are unchanged. "No retained selectivity result" is used throughout, including headings and SI summaries, and never "never evaluated" or "outside the scan". The empty stored-label intersection is scoped to the **classic subset**; the full retained intersection contains DLL3. Unavailable-evidence states, a measured non-significant contrast and a significant decrease are three different things, and a significant decrease is a measured negative contrast |
| R4 | "Every number in this manuscript is reproducible offline"; the sequencing artifact held "group-level peak summaries"; the "sequencing reductions" could be recalculated from the retained grouped summaries; the statistics generator "depends on `accession-symbol-cache.json`" | The artifact retains **final gene-level arm medians with peak and library counts**. From them a reader can retrieve those medians and compute ratios and descriptive bands; the two-stage reduction that produced them — median across libraries per peak, then median across a gene's peaks — **cannot** be recalculated, because the per-library values and the separate per-peak arm medians are not retained. Retained per-sample derived array values remain recalculable. `accession-symbol-cache.json` is upstream probe-to-symbol mapping provenance, not a runtime dependency of the statistics step, whose declared inputs are the two panel JSONs |
| R5 | Surrogate-based target lists "are routinely built for rare tumours" and their outcomes "rarely reported"; prioritisation "for this disease" has run on lineage surrogates; SSTR2 and GD2 were "absent from previous EMC surface discussions"; "the first EMC transcript readings" | Frequency, prior-absence and priority statements are limited to the bounded retrieval described in Methods and to this programme's own chronology. The deposits reanalysed here are credited as prior work by their depositors. No further search was made for this batch |
| R6 | "The 17 available panel tests" (main Results, SI Table S5 caption, SI Note S5, Appendix A7 register) | **16 scored panel contrasts: nine on GPL6244 and seven on GPL3290.** The somatostatin-receptor family and the HLA-presented-intracellular-antigen panels fall below the coverage floor on GPL3290, emit no score there, and remain unscored. Every panel value in Table S5 is unchanged, and no score or test was added to justify the superseded count. The erratum is the reviewer's and the adjudicating root's own, inherited from the accepted baseline; it is corrected here rather than attributed to a later author. The substantive qualification — panels are exploratory and uncorrected, and no joint replicability FDR was estimated — is unchanged |
| R7 | The local reproducibility packet's two manuscript entries were the pre-correction 99,615-byte main and 41,853-byte SI | The revised pair is bound as current by exact path, bytes and SHA256 in the residual batch's current-packet record, with the baseline pair retained as historical inputs and the packet manifest left unedited as a dated historical identity record. The already-held GEO summary record `geo_esummary_emc.txt` (30,740 B) is located exactly there; it carries sample titles and source PMIDs and does **not** provide a probe audit or the primary papers' full texts. No public immutable release locator exists, none is claimed, and none is a prerequisite for this local packet |
| R8 | The F03 aggregation-order annotation was **specified, not applied** | The sole integrating parent applied it once, on 2026-09-08, as an annotation-only additive change to `gse28866-tumour-vs-normal.json` and the `_contrast` literal in `gse28866_tumour_vs_normal.py`, with the superseded string retained verbatim inside the artifact. The whole JSON was compared leaf by leaf in both directions: two keys added, one value changed, none removed, and no leaf moved outside the three annotation keys. No producer, normalisation, recalibration, inversion or renderer was executed. The dated packet manifest still records the pre-correction identities and is valid as history of what was checked when |

⚠ **What this residual batch does not establish.** It adds no measurement and repairs no missing
evidence. The broader validated normal-tissue window, a quantified transfer task, a calibrated null,
an identified compartment, absolute surface abundance and any clinical prioritisation remain
unavailable on the evidence and design conditions already recorded. This batch narrows the claims to
what the retained records support; it does not lift the hold on the stronger ones.

"""

def main():
    t = MAIN.read_text(encoding="utf-8")
    print("READ  %s  %d B  sha256 %s" % (MAIN.name, len(t.encode()), hashlib.sha256(t.encode()).hexdigest()))
    if t.count(ANCHOR) != 1:
        print("FAILED — anchor matched %d times, need exactly 1. Nothing written." % t.count(ANCHOR))
        return 1
    if "Appendix A8" in t:
        print("FAILED — Appendix A8 already present. Nothing written.")
        return 1
    t = t.replace(ANCHOR, BLOCK + ANCHOR, 1)
    MAIN.write_text(t, encoding="utf-8")
    b = MAIN.read_bytes()
    print("WROTE %s  %d B  sha256 %s" % (MAIN.name, len(b), hashlib.sha256(b).hexdigest()))
    print("TOTAL EDITS: 1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
