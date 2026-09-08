#!/usr/bin/env python3
"""P-ST residual batch R1-R8, 2026-09-08.

Exact-match, whole-file edits on the candidate revised pair. Every anchor must match
EXACTLY ONCE or the script exits non-zero WITHOUT writing anything. No anchor is ever
loosened to obtain a match.
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REV = ROOT / "P-ST-correction/revised"
MAIN = REV / "emc-surface-target-landscape.md"
SI = REV / "emc-surface-target-landscape-si.md"

E = []  # (file, residual, old, new)


def edit(f, r, old, new):
    E.append((f, r, old, new))


# ---------------------------------------------------------------- R5
edit(MAIN, "R5", """into a map that this work's bounded prior-art retrieval could find, and prioritisation for this disease
has in practice run on lineage surrogates.""",
"""into a map that this work's bounded prior-art retrieval could find, and prioritisation in this
programme has in practice run on lineage surrogates.""")

edit(MAIN, "R5", """for. Surrogate-based target lists are routinely built for rare tumours, and the outcome when the
tumour itself is measured is rarely reported.""",
"""for. This programme built its surrogate-based list that way, and what follows is the outcome when the
tumour itself was measured. No claim is made here about how often such lists are built elsewhere, or
about how often their outcomes are reported: the bounded retrieval described above cannot support a
field-wide frequency statement in either direction.""")

edit(MAIN, "R5", """EMC's reported neuroendocrine differentiation motivated two candidate targets absent from previous EMC
surface discussions: SSTR2""",
"""EMC's reported neuroendocrine differentiation motivated two candidate targets that this work's bounded
prior-art retrieval did not find addressed in EMC surface discussions: SSTR2""")

# ---------------------------------------------------------------- R1
edit(MAIN, "R1", """An antigen
carried only by stroma reads at the floor, demonstrated by LRRC15, an established sarcoma
cancer-associated-fibroblast antigen with a clinical antibody-drug conjugate programme behind it, at
`frac_expressed` 0.0; the limit is narrower than "the scan cannot see stroma", because CD248 and
PDGFRB, also called stromal antigens, are selectivity-significant here.""",
"""An antigen
carried only by stroma has no compartment in this population in which it could be counted. LRRC15, an
established sarcoma cancer-associated-fibroblast antigen with a clinical antibody-drug conjugate
programme behind it, reads at `frac_expressed` 0.0, which means that no scanned line exceeded the
chosen expression threshold: a threshold result, not a calibrated detector floor, and not a
demonstration that a missing compartment caused the reading. FAP reads at `frac_expressed` 0.16 with
0.56 of class lines detectable, so it is not measured here as a stroma-only antigen. CD248 and PDGFRB,
also called stromal antigens, are selectivity-significant here, which shows there is something in the
culture to measure and does not resolve which compartment contributes their signal in bulk tumour.
Missing compartment coverage is one explanation compatible with these readings rather than a cause
separated from the alternatives by any measurement here.""")

edit(MAIN, "R1", """FAP needs a further caution, and CD248 shows where that caution stops. The surrogate instrument holds
no fibroblast compartment, and an antigen that only fibroblasts carry reads at the floor: LRRC15, an
established sarcoma fibroblast antigen, reads at an expressed fraction of 0.0, and FAP at 0.16. A
verdict on FAP from this instrument is therefore a statement about tumour cells in culture rather than
about FAP in an EMC tumour. CD248 and PDGFRB, also called stromal antigens, are selectivity-significant
here because mesenchymal tumour cells transcribe them, so their readings are not subject to the same
caution.""",
"""FAP needs a further caution. The surrogate instrument's scanned population is monoculture and holds no
fibroblast compartment, so an antigen carried only by fibroblasts has no compartment here in which it
could be counted. LRRC15, an established sarcoma fibroblast antigen, reads at an expressed fraction of
0.0 — no scanned line exceeded the chosen threshold — while FAP reads at an expressed fraction of 0.16
with 0.56 detectable, so FAP is not measured here as a stroma-only antigen. A verdict on FAP from this
instrument is a statement about tumour cells in culture rather than about FAP in an EMC tumour. CD248
and PDGFRB, also called stromal antigens, are selectivity-significant here, which shows that
mesenchymal tumour cells transcribe them in culture; it does not identify which compartment
contributes their signal in a bulk EMC tumour, so their bulk-tissue readings carry the same
compartment ambiguity. Missing compartment coverage remains a compatible explanation for the low
stromal-antigen readings and is not an identified cause. The separate limitation that no scanned line
supplies authenticated EMC evidence is stated in Appendix A and is not merged into this one.""")

# ---------------------------------------------------------------- R4
edit(MAIN, "R4", """none is accountable for the work. Every number in this manuscript is reproducible offline from the
artifacts named in the data availability statement, without any language model.""",
"""none is accountable for the work. The numbers reported in this manuscript are traceable to the
artifacts named in the data availability statement, which state exactly what can and cannot be
recalculated from them; no language model is required for any of it.""")

edit(MAIN, "R4", """recalculated offline is stated exactly under Data availability: the retained derived records support
recalculation of the reported contrasts, corrections and reductions, while the surrogate scan's complete
gene universe, its per-line observations and its rank-test *p* values, the full probe-annotation audit
trail for the arrays, and the original sequencing peak table are **not** in hand, so the results that
depend on those inputs are not independently reproducible from what is released.""",
"""recalculated offline is stated exactly under Data availability: the retained derived records support
recalculation of the reported array contrasts and corrections, and retrieval of the final gene-level
sequencing medians together with ratio and descriptive-band arithmetic over them, while the per-library
values and per-peak arm medians that the sequencing reduction consumed, the surrogate scan's complete
gene universe, its per-line observations and its rank-test *p* values, the full probe-annotation audit
trail for the arrays, and the original sequencing peak table are **not** in hand, so the results that
depend on those inputs are not independently reproducible from what is released.""")

edit(MAIN, "R4", """(`per_gene.values`), which retains **group-level peak summaries and not per-sample values** — an earlier
version of this statement described the sequencing artifact as carrying per-sample values and was
wrong.""",
"""(`per_gene.values`), which retains **final gene-level arm medians with peak and library counts, and not
per-sample or per-peak values** — an earlier version of this statement described the sequencing
artifact as carrying per-sample values and was wrong, and a later one described it as carrying
group-level peak summaries, which invited the same misreading.""")

edit(MAIN, "R4", """the cross-platform state assignments; the three sensitivity summaries; the panel scores; and the
sequencing reductions from the retained grouped summaries. A reader **cannot** reproduce, from anything
released here: the surrogate scan's rank-test *p* and *q* values,""",
"""the cross-platform state assignments; the three sensitivity summaries; the panel scores; and, from the
retained final gene-level sequencing medians, retrieval of those medians together with ratio and
descriptive-band arithmetic over them. A reader **cannot** reproduce, from anything released here: the
two-stage sequencing reduction that produced those medians — the median across libraries per peak,
then the median across a gene's peaks — because the per-library values and the separate per-peak arm
medians are not retained; the surrogate scan's rank-test *p* and *q* values,""")

edit(MAIN, "R4", """`emc_tissue_read_statistics.py`, which consumes `emc-expression-panels.json` and
`emc-expression-panels-inputs.json` and depends on `accession-symbol-cache.json` for probe-to-symbol
resolution.""",
"""`emc_tissue_read_statistics.py`, which consumes `emc-expression-panels.json` and
`emc-expression-panels-inputs.json`; those two files are its declared inputs and the only files its
main reads, and it imports only the standard library. `accession-symbol-cache.json` is upstream
probe-to-symbol mapping provenance for those inputs and is carried in the packet for that reason; it is
not a runtime dependency of this statistics step.""")

# ---------------------------------------------------------------- R3
edit(MAIN, "R3", """Two nested sets are reported throughout, and they are different estimands rather than competing
answers. The **classic-antigen subset** is the long-standing protein antigens listed in Table 1, the ones a
reader of the sarcoma target literature would expect to see scored. The **retained actionable-antigen
set** is all 47 antigens the scan carries a per-gene row for, and it contains the classic subset.""",
"""Two overlapping sets are reported throughout, and they are different estimands rather than competing
answers. The **classic-antigen subset** is the 18 long-standing protein antigens listed in Table 1, the ones a
reader of the sarcoma target literature would expect to see scored. The **retained actionable-antigen
set** is all 47 antigens the scan carries a per-gene row for. The two sets **overlap in 15 antigens and
neither contains the other**: CSPG4, B4GALNT1 and SSTR2 are classic antigens with no retained
selectivity row.""")

edit(MAIN, "R3", """### CSPG4, a gene outside the stage-1 scan""",
"""### CSPG4, a gene with no retained selectivity result""")

edit(MAIN, "R3", """It is
present in the normal-tissue annotation artifact, so "absent from the surrogate instrument's retained
selectivity rows" is the exact statement and "absent from every committed artifact" is not. Its absence
from the empty selective-and-restricted intersection is therefore a measured coverage gap rather than a
rejection.""",
"""It is
present in the normal-tissue annotation artifact, so "no retained selectivity result" is the exact
statement and "absent from every committed artifact" is not. Its absence from the empty
selective-and-restricted intersection of the **classic subset** — the full retained intersection is not
empty and contains DLL3 — is therefore a measured coverage gap rather than a rejection.""")

edit(MAIN, "R3", """These
missing-evidence states are distinct and are kept distinct throughout: no normal-tissue record; no
retained selectivity result; no row on the tissue board; a contrast excluded for insufficient comparator
observations; a measured but non-significant contrast; and a significant decrease. None of them is a low
or negative reading.""",
"""These
states are distinct and are kept distinct throughout. Four of them are unavailable-evidence states: no
normal-tissue record; no retained selectivity result; no row on the tissue board; and a contrast
excluded for insufficient comparator observations. None of those four is a low or negative reading. A
measured but non-significant contrast is a measurement that did not meet the *q* decision rather than
an unavailable one, and **a significant decrease is a measured negative contrast**: it is a low reading
in that comparison, it must not be relabelled as missing evidence, and it establishes no absence.""")

# ---------------------------------------------------------------- R2
edit(MAIN, "R2", """normal cells, so this result removes a transcriptomic rationale for treating B7-H3 as the obvious first
choice and settles nothing about the protein either way.""",
"""normal cells. What this result establishes is that these particular contrasts provide no significant
evidence of upward enrichment for B7-H3; no target-selection utility, equivalence bound, ranking
accuracy or protein criterion has been defined here that would license removing the transcriptomic case
for it, and it settles nothing about the protein either way.""")

edit(MAIN, "R2", """non-significant on both, which means *q* >= 0.05 on each platform and not that the antigen is absent: on
GPL3290 the median half-width of the ordinary 95 % interval is 0.957 standard deviation units, so a
non-significant row there is compatible with a substantial difference in either direction.""",
"""non-significant on both, which means *q* >= 0.05 on each platform and not that the antigen is absent.
Each row's own pointwise interval, printed in Table 3, states what that row's data exclude; the GPL3290
median half-width of 0.957 standard deviation units describes typical imprecision on that platform and
does not determine any particular gene's interval, and some non-significant rows have intervals that
exclude zero.""")

edit(MAIN, "R2", """FAP. It indicates instead that a FAP-directed route cannot claim EMC as a selectively FAP-rich
indication among soft-tissue tumours; the whole 13-gene stromal and matrix panel has a negative point""",
"""FAP. What these particular contrasts establish is the absence of statistically significant evidence
that EMC is FAP-rich relative to these comparator arms; that is not a route-level or indication
decision, and no equivalence test was performed, so the negative non-significant panel estimate bounds
nothing. The whole 13-gene stromal and matrix panel has a negative point""")

edit(MAIN, "R2", """neuroendocrine phenotype might extend to SSTR2 surface expression at a level worth imaging, and the
first EMC transcript readings show no elevation over other soft-tissue tumours and no striking
absolute signal. The gate is unchanged: a peptide-receptor radioligand route depends on absolute
receptor protein density and on the tumour-to-normal uptake ratio, and no quantity in this study
measures either. A single somatostatin-receptor
positron-emission-tomography scan, or an SSTR2 immunohistochemical stain on archival EMC, remains the
cheap decisive measurement, and these readings lower the prior for it rather than removing the reason to
perform it.""",
"""neuroendocrine phenotype might extend to SSTR2 surface expression at a level worth imaging; the EMC
transcript readings reported here show no significant elevation over the comparator soft-tissue
tumours, and cross-probe rank and transformed summary scores cannot express an absolute receptor level
in either direction. The gate is unchanged: a peptide-receptor radioligand route depends on absolute
receptor protein density and on the tumour-to-normal uptake ratio, and no quantity in this study
measures either. A single somatostatin-receptor positron-emission-tomography scan would observe tracer
uptake in the material scanned, and an SSTR2 immunohistochemical stain would observe protein and its
localisation in the sampled tissue; either would be cheap, and neither would decide population
expression, a therapeutic window, or the suitability of the route. These readings lower the prior for
such a measurement rather than removing the reason to perform it.""")

edit(MAIN, "R2", """significantly on GPL6244 (Δ = +0.885, *t* = 7.42, 95 % CI 0.61 to 1.16, *q* = 0.0017) and is flat on
GPL3290 (Δ = −0.189, *t* = −0.40, 95 % CI −1.23 to 0.86, *q* = 0.764), where the interval is wide
enough to be compatible with a substantial change in either direction. The classifier records this as movement on one platform with
flatness on the other rather than as opposite signs, because the GPL3290 value is negative in sign but
flat in magnitude. The row does not replicate and is also not contradicted.""",
"""significantly on GPL6244 (Δ = +0.885, *t* = 7.42, 95 % CI 0.61 to 1.16, *q* = 0.0017) and is
non-significant on GPL3290 (Δ = −0.189, *t* = −0.40, 95 % CI −1.23 to 0.86, *q* = 0.764), a negative
point estimate whose interval runs from −1.23 to +0.86 and therefore excludes little in either
direction. The stored classifier label records this as movement on one platform with "flatness" on the
other rather than as opposite signs, because the GPL3290 estimate is negative in sign and small in
magnitude; that label is a banding convention over an imprecise non-significant estimate, not an
equivalence result, and it does not establish a biologically flat or silent state. The row does not
replicate and is also not contradicted.""")

edit(MAIN, "R2", """That third
reason was tested. In the reference-matched sensitivity analysis, which drops the three
gastrointestinal stromal tumour arrays and leaves ten EMC against three dermatofibrosarcoma
protuberans arrays processed the same way, CSPG4 is Δ = −0.518, *t* = −1.84, 95 % CI −1.15 to 0.11,
*q* = 0.182 — still not significant, still not positive, and so the processing mismatch does not by
itself account for the flat GPL3290 contrast.""",
"""That third
reason was examined in a recorded sensitivity analysis. Dropping the three
gastrointestinal stromal tumour arrays and leaving ten EMC against three dermatofibrosarcoma
protuberans arrays processed the same way, CSPG4 is Δ = −0.518, *t* = −1.84, 95 % CI −1.15 to 0.11,
*q* = 0.182: after excluding the mismatched samples the point estimate stays negative and the contrast
stays non-significant. That is what the recorded analysis did. A non-significant result in a
three-versus-ten comparison does not settle whether the processing mismatch contributes to the GPL3290
contrast.""")

edit(MAIN, "R2", """and the other-sarcoma medians as untested ratios; taken together those readings remove the
transcriptomic case for treating it as the obvious first EMC address and do not establish that it is
low, absent, or unsuitable.""",
"""and the other-sarcoma medians as untested ratios; taken together those readings supply no significant
evidence of upward enrichment that would support treating it as the obvious first EMC address. They do
not remove the transcriptomic case for it, and they do not establish that it is low, absent, or
unsuitable.""")

edit(MAIN, "R2", """interval is 0.259 standard deviation units on GPL6244 and 0.957 on GPL3290 — full widths of about 0.52
and 1.90 — so a non-significant row on GPL3290 excludes very little and should be read as uninformative
rather than as an absence.""",
"""interval is 0.259 standard deviation units on GPL6244 and 0.957 on GPL3290 — full widths of about 0.52
and 1.90 — so non-significant rows on GPL3290 are typically imprecise. That median describes the
platform and does not determine any particular gene's interval: each row's own printed interval states
what that row excludes, and 14 GPL6244 and 8 GPL3290 non-significant rows have intervals excluding
zero.""")

edit(MAIN, "R2", """The decisive missing datum is now **protein and surface localisation**, plus a cohort large enough to carry a distribution |""",
"""The missing measurements are now **protein and surface localisation**, plus a cohort large enough to carry a distribution |""")

# ---------------------------------------------------------------- R6
edit(MAIN, "R6", """entered into any multiplicity correction: the 17 available panel tests across the nine curated panels are
uncorrected and exploratory (Supplementary Table S5).""",
"""entered into any multiplicity correction: the **16 scored panel contrasts** across the nine curated
panels — nine on GPL6244 and seven on GPL3290 — are uncorrected and exploratory (Supplementary
Table S5). The somatostatin-receptor family and the HLA-presented-intracellular-antigen panels fall
below the coverage floor on GPL3290, emit no score there, and are therefore not tests.""")

edit(MAIN, "R6", """The 17 available panel tests are exploratory and uncorrected, with differing membership and coverage between platforms.""",
"""The panel contrasts are exploratory and uncorrected, with differing membership and coverage between platforms. ⚠ **Erratum, 2026-09-08:** the count is **16 scored contrasts** — nine on GPL6244 and seven on GPL3290 — not the 17 stated here previously; the somatostatin-receptor family and HLA-presented-intracellular-antigen panels are unscored on GPL3290 and stay unscored. The superseded number originated in the review this batch answers and was carried into the first revision; no score or test has been added, and every panel value is unchanged.""")

# ================================================================ SI
edit(SI, "R3", """For each scanned gene the artifact records the class mean, the fraction of class lines expressing it, the""",
"""For each gene carried in the artifact's retained selected output the artifact records the class mean, the fraction of class lines expressing it, the""")

edit(SI, "R6", """two-sided value for that panel's own score. ⚠ **The 17 available panel tests below are exploratory and
uncorrected**:""",
"""two-sided value for that panel's own score. ⚠ **The 16 scored panel contrasts below — nine on GPL6244
and seven on GPL3290 — are exploratory and uncorrected**:""")

edit(SI, "R6", """so the 17 available panel tests are exploratory and uncorrected. Intersecting the two separately""",
"""so the 16 scored panel contrasts — nine on GPL6244 and seven on GPL3290 — are exploratory and
uncorrected. Intersecting the two separately""")

edit(SI, "R2", """correction: the median **half-width** of the ordinary 95 % interval is 0.957 standard deviation units on
GPL3290, a full width of about 1.90, so a non-significant row there excludes very little and the
two-platform rule is governed by that platform.""",
"""correction: the median **half-width** of the ordinary 95 % interval is 0.957 standard deviation units on
GPL3290, a full width of about 1.90, so non-significant rows there are typically imprecise and the
two-platform rule is governed by that platform. That median describes the platform and does not
determine any particular gene's interval; each row's own interval is printed in Table S7.""")

edit(SI, "R2", """The PRAME normal median is zero, so its ratio against normal tissue is undefined and is not reported. A
cancer-testis antigen being absent from normal organs is expected and says nothing about this disease.""",
"""The PRAME normal median is zero, so its ratio against normal tissue is undefined and is not reported.
That zero is the median of a pooled, unequally weighted adult and fetal panel: it is not evidence that
PRAME is absent from every contributing library or organ, still less from all normal organs. A low
pooled summary score for a cancer-testis antigen is unsurprising and says nothing about this disease.""")

edit(SI, "R1", """**L2, the stromal floor demonstrated.** LRRC15,""",
"""**L2, what stroma-associated antigens read in this instrument.** LRRC15,""")

edit(SI, "R1", """an expressed fraction of 0.24 and *q* = 0.0001; both are selectivity-significant. These values show what
a stroma-only antigen looks like in this instrument, which is indistinguishable from a genuinely absent
one. They also narrow the limit, and the narrower version is the one this study uses. CD248 and PDGFRB
are routinely called stromal or pericyte antigens and both read significant here, because mesenchymal
tumour cells genuinely transcribe them and there is therefore something in the culture to measure. The
limit is not that the scan cannot see stroma; it is that the scan cannot see a gene that **only** the
stroma expresses. LRRC15 and FAP are that case and CD248 and PDGFRB are not.""",
"""an expressed fraction of 0.24 and *q* = 0.0001; both are selectivity-significant. An expressed fraction
of 0.0 means that no scanned line exceeded the chosen threshold: a threshold result, not a calibrated
detector floor, and one that does not distinguish an absent transcript from one below the threshold.
FAP's 0.16 expressed and 0.56 detectable fractions show that FAP is not measured here as a stroma-only
antigen at all. CD248 and PDGFRB are routinely called stromal or pericyte antigens and both read
significant here, which shows that mesenchymal tumour cells transcribe them in culture and that there
is therefore something in the culture to measure; it does not identify which compartment contributes
their signal in a bulk EMC tumour, so their bulk readings carry the same compartment ambiguity as the
others. The limit this study uses is that a population containing no stromal compartment cannot count
an antigen carried only by stroma. Missing compartment coverage is therefore one explanation compatible
with the low LRRC15 reading, not a cause separated from the alternatives by any measurement here.""")

edit(SI, "R3", """the correct current reading is that CSPG4 is absent from the
**selectivity scan** and present in the **normal-tissue prior**.""",
"""the correct current reading is that CSPG4 has **no retained
selectivity result** in the selectivity scan and is present in the **normal-tissue prior**.""")

edit(SI, "R3", """selected output is not proof that the scan never evaluated it. Its absence from the
selective-and-restricted intersection is therefore a coverage gap and not a rejection.""",
"""selected output is not proof that the scan never evaluated it. Its absence from the classic subset's
empty selective-and-restricted intersection — the full retained intersection is not empty and contains
DLL3 — is therefore a coverage gap and not a rejection.""")

edit(SI, "R3", """CSPG4 is the largest absolute row in the sequencing deposit and a gene the surrogate stage never
evaluated. The main text states its values. Two points bear repeating here.""",
"""CSPG4 is the largest row in the sequencing deposit on the deposit's compressed score scale, and a gene
for which the surrogate stage retains **no selectivity result**; whether it was ever scanned is
undecidable from the retained artifact. The main text states its values. Two points bear repeating
here.""")

edit(SI, "R2", """The classifier records movement on one platform with flatness on the other, rather than opposite signs,
because the GPL3290 value is negative in sign but flat in magnitude. The distinction licenses different
next steps: "strongly up here, silent there" is a row that does not replicate, while "up here, down
there" would be a row that is contradicted.""",
"""The stored classifier label records movement on one platform with "flatness" on the other, rather than
opposite signs, because the GPL3290 estimate is negative in sign and small in magnitude
(Δ = −0.189, 95 % CI −1.23 to +0.86, *q* = 0.764). That label is a banding convention applied to an
imprecise non-significant estimate; it is not an equivalence result, it does not establish a
biologically flat or silent state, and it does not by itself license a different next step. What the
data show is a significant increase on one platform and an imprecise non-significant estimate on the
other: a row that does not replicate and is also not contradicted.""")

edit(SI, "R3", """SSTR2 have no retained selectivity result, which is not the same as never having been evaluated. None of
these states is a low, negative or absent reading, and no statement in either document treats any of them
as one; a measured but non-significant contrast and a significant decrease are two further, different
states.""",
"""SSTR2 have no retained selectivity result, which is not the same as never having been evaluated. None of
these unavailable-evidence states is a low, negative or absent reading, and no statement in either
document treats any of them as one. A measured but non-significant contrast and a significant decrease
are two further, different states: the first is a measurement that did not meet the *q* decision, and
the second **is** a measured negative contrast — a low reading in that comparison, which establishes no
absence and must not be relabelled as missing evidence.""")

edit(SI, "R4", """**Reproducibility is partial and its boundary is stated.** The retained derived records support offline
recalculation of the array contrasts, intervals, within-platform corrections, cross-platform states,
sensitivity summaries, panel scores and sequencing reductions. They do **not** support reproduction of
the surrogate scan's rank-test""",
"""**Reproducibility is partial and its boundary is stated.** The retained derived records support offline
recalculation of the array contrasts, intervals, within-platform corrections, cross-platform states,
sensitivity summaries and panel scores, and retrieval of the final gene-level sequencing medians with
ratio and descriptive-band arithmetic over them. They do **not** support recalculation of the two-stage
sequencing reduction — the median across libraries per peak, then the median across a gene's peaks —
because the per-library values and the separate per-peak arm medians are not retained; nor reproduction
of the surrogate scan's rank-test""")


def main():
    texts = {}
    for path in (MAIN, SI):
        texts[path] = path.read_text(encoding="utf-8")
        print("READ  %s  %d B  sha256 %s" % (path.name, len(texts[path].encode()),
                                             hashlib.sha256(texts[path].encode()).hexdigest()))
    failures = []
    for i, (path, res, old, new) in enumerate(E, 1):
        n = texts[path].count(old)
        if n != 1:
            failures.append("EDIT %02d (%s, %s): anchor matched %d times, need exactly 1 :: %r"
                            % (i, res, path.name, n, old[:90]))
            continue
        if new in texts[path]:
            failures.append("EDIT %02d (%s, %s): replacement text already present" % (i, res, path.name))
            continue
        texts[path] = texts[path].replace(old, new, 1)
        print("EDIT %02d  %-3s  %-34s  -%d +%d chars" % (i, res, path.name, len(old), len(new)))
    if failures:
        print("\nFAILED — nothing written:")
        for f in failures:
            print("  " + f)
        return 1
    for path in (MAIN, SI):
        path.write_text(texts[path], encoding="utf-8")
        b = path.read_bytes()
        print("WROTE %s  %d B  sha256 %s" % (path.name, len(b), hashlib.sha256(b).hexdigest()))
    print("\nTOTAL EDITS: %d" % len(E))
    return 0


if __name__ == "__main__":
    sys.exit(main())
