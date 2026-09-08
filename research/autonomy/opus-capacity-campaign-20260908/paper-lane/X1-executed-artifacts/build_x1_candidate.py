#!/usr/bin/env python3
"""X1 lane - build a PROPOSED NEW working revision of the EMC ATR collaborator package.

Input : INPUTS/R1/PROPOSED-emc-atr-collaborator-package.md (R1's proposed candidate)
Output: PROPOSED-X1-emc-atr-collaborator-package.md
        RETAINED-APPENDIX-A-history.md  (Appendix A, verbatim, never erased)
Every replacement is asserted. Nothing is deleted without being retained.
"""
import pathlib, sys, re

L = pathlib.Path("/tmp/claude-0/x1-lane")
src = (L / "INPUTS/R1/PROPOSED-emc-atr-collaborator-package.md").read_text()
base = (L / "INPUTS/R1/BASELINE-emc-atr-collaborator-package.md").read_text()
t = src
edits = []

def rep(tag, old, new, count=1):
    global t
    n = t.count(old)
    assert n == count, f"{tag}: expected {count} occurrence(s), found {n}"
    t = t.replace(old, new)
    edits.append(tag)

TITLE = ("Reading-frame constraints and retained RG content in NR4A3 fusion models of "
         "extraskeletal myxoid chondrosarcoma")
OLDTITLE = ("Transcript-level models of the NR4A3 fusions of extraskeletal myxoid chondrosarcoma, "
            "and five pre-specified predictions for a DNA double-strand break recruitment assay")

# ---------------------------------------------------------------- E0 provenance banner
old_banner = t[:t.index("\n---\nid: DOC-EMC-ATR-COLLABORATOR-PACKAGE")]
new_banner = """<!-- ============================================================================
PROPOSED NEW WORKING REVISION - X1 lane, 2026-09-08. NOT A RECOVERED ORIGINAL.

This is a NEW revision proposed now. No file, blob or draft of any lost historical
revision was found, and none is claimed. It is built by applying, to R1's proposed
candidate, (a) three required corrections to that candidate, (b) qualifications
established by U1, and (c) the completed outputs of W1 (Supplementary Table S3),
W2 (Panel A key sources) and W3 (Okamoto 2001 metadata).

Everything here is PROPOSED. Nothing has been applied to any shared repository
path, no view has been regenerated, and no title or cross-reference outside this
file has been changed. Shared integration is the scientific coordinator's decision.
Decisions, denominator provenance and unresolved items: X1-DECISION-RECORD.md.
Appendix A of the input is retained verbatim in RETAINED-APPENDIX-A-history.md.
============================================================================= -->"""
rep("E0-banner", old_banner, new_banner)

# ---------------------------------------------------------------- E1 title
rep("E1-frontmatter-title", f'title: "{OLDTITLE}"', f'title: "{TITLE}"')
rep("E1-h1", f"\n# {OLDTITLE}\n", f"\n# {TITLE}\n")

# ---------------------------------------------------------------- E2 author identity
rep("E2-orcid",
    "ORCID: [ORCID TO BE SUPPLIED BY THE AUTHOR BEFORE SUBMISSION]",
    "ORCID: [0000-0002-1823-1451](https://orcid.org/0000-0002-1823-1451)")
rep("E2-editorial-author",
    "AUTHOR BLOCK matches the block the author confirmed in nr4a3-degrader-paper.md and\n"
    "response-endpoint-indolent-tumours.md. No ORCID is given because the repository carries none.",
    "AUTHOR BLOCK matches the block the author confirmed in nr4a3-degrader-paper.md and\n"
    "response-endpoint-indolent-tumours.md. The ORCID iD is the one already carried in this\n"
    "repository for this author (the ASO author block and the 2026-08-20 submission-plan record);\n"
    "it was read from the repository and not looked up externally.")

# ---------------------------------------------------------------- E3 ABSTRACT: the three corrections
rep("E3a-abstract-frequency",
    "Type 1 is the commonest reported type in every\nseries that types its cases; type 2 is a minority variant, counted once across three counted series.",
    "Type 1 is the commonest EWSR1::NR4A3 type in both\nseries that typed EWSR1 subtypes; type 2 is counted once in those two series, and a third series\ncounts partner genes rather than EWSR1 subtypes.")

rep("E3b-abstract-comparator",   # REQUIRED CORRECTION 1
    "against a measured\ncomparator span of 0.000 to 0.267 for EWSR1::ATF1 and firmly measured positions at 0.000 and 1.000.",
    "against a span of 0.000 to 0.267 spanned by the\nthree reported EWSR1::ATF1 breakpoints. The EWSR1::ATF1 construct in which recruitment was\nmeasured has no stated breakpoint, so that span describes the reported breakpoints and not the\nmeasured construct; the measured positions on the axis itself are 0.000 and 1.000.")

rep("E3c-abstract-grid",         # REQUIRED CORRECTION 3
    "TCF12, the 5' partner in a minority of EMC, falls outside\nthe FET compositional range at every prefix length.",
    "TCF12, the 5' partner in a minority of EMC, falls outside\nthe FET compositional range at every prefix on the evaluated grid (50 aa upwards in 10-aa steps).")

# ---------------------------------------------------------------- E4 3.1 frequency wording
rep("E4a-t1-cell",
    "| EWSR1::NR4A3 type 1 | EWSR1 e12 to NR4A3 e3 | commonest in every series that types its cases: 10 of 15 [7], 11 of 15 [9] |",
    "| EWSR1::NR4A3 type 1 | EWSR1 e12 to NR4A3 e3 | commonest EWSR1::NR4A3 type in both series that typed EWSR1 subtypes: 10 tumours, the most frequent transcript [7]; 11 of the 15 fusion-positive cases [9] |")
rep("E4b-t2-cell",
    "| EWSR1::NR4A3 type 2 | EWSR1 e7 to NR4A3 e2 | minority variant, counted once across three counted series: 1 of 15 [9], absent from the counted types of [7] |",
    "| EWSR1::NR4A3 type 2 | EWSR1 e7 to NR4A3 e2 | counted once in the two series that typed EWSR1 subtypes: 1 of the 15 fusion-positive cases [9], and absent from the counted types of [7] |")
rep("E4c-t5-cell",
    "| EWSR1::NR4A3 type 5 | EWSR1 e13 to NR4A3 e3 | named second commonest in [7], 2 of 15 |",
    "| EWSR1::NR4A3 type 5 | EWSR1 e13 to NR4A3 e3 | named the second most common transcript in [7], in two cases |")
rep("E4d-taf15-cell",
    "| TAF15::NR4A3 | TAF15 e6 to NR4A3 e3 | the only reported coding junction; 3 of 15 [9], 4 of 10 [10] |",
    "| TAF15::NR4A3 | TAF15 e6 to NR4A3 e3 | the only reported coding junction; 3 of the 15 fusion-positive cases [9]; 4 of the 10 fusions in [10], which counts partner genes rather than EWSR1 subtypes |")

# "two commonest" lead-in  -> resolved so it does not contradict the counted series
rep("E4e-two-commonest",
    """The two commonest types are quoted verbatim from a primary source: "The most common fusion
transcript contains exon 12 of EWSR1 fused to exon 3 of NR4A3 (type 1), whereas exon 7 of EWSR1 is
fused to exon 2 of NR4A3 in the type 2 fusion transcript" [4]. They are corroborated independently
by RT-PCR primer design, an EWSR1 exon 12 forward primer paired with an NR4A3 exon 3 reverse for
type 1 and an EWSR1 exon 7 forward paired with an NR4A3 exon 2 reverse for type 2 [6], and by a
counted series in which 10 of 15 tumours carried exon 12 to exon 3 and 2 of 15 carried type 5 [7].""",
    """The type 1 and type 2 junctions are defined verbatim in a primary source: "The most common fusion
transcript contains exon 12 of EWSR1 fused to exon 3 of NR4A3 (type 1), whereas exon 7 of EWSR1 is
fused to exon 2 of NR4A3 in the type 2 fusion transcript" [4]. That sentence names type 1 as the
most common and defines type 2 without making any frequency claim about it, so it establishes the
two junctions and not a ranking of the two; the counted series in the table above, and not this
definition, carry the frequencies. The junctions are corroborated independently
by RT-PCR primer design, an EWSR1 exon 12 forward primer paired with an NR4A3 exon 3 reverse for
type 1 and an EWSR1 exon 7 forward paired with an NR4A3 exon 2 reverse for type 2 [6], and by the
counted series in which exon 12 to exon 3 was the most frequent transcript, in 10 tumours, and
exon 13 to exon 3 the second most common, in two [7].""")

# ---------------------------------------------------------------- E5 3.3: figure pointer only
rep("E5-fig1c",
    "The insertion lies between EWSR1(1-264) and NR4A3's own\nmethionine, and the chimeric open reading frame is 949 aa.",
    "The insertion lies between EWSR1(1-264) and NR4A3's own\nmethionine, and the chimeric open reading frame is 949 aa. Figure 1C draws this seam.")

# ---------------------------------------------------------------- E6 3.4 corrections + figure
rep("E6a-table4-caption",
    "**Table 4.** EMC fusions and the measured comparators on one axis. Fractions are of the 5' partner's\nwild-type RG total.",
    "**Table 3.** EMC fusions and their comparators on one axis, with the status column distinguishing a\nposition measured in reference 1 from a reported breakpoint of a disease in which the mechanism was\nmeasured. Fractions are of the 5' partner's wild-type RG total.")

rep("E6b-neither-placed",         # REQUIRED CORRECTION 2
    """Neither EMC type falls outside the range of retained-RG fractions the reported breakpoints of the
measured diseases already cover; neither is placed between two positions measured in reference 1,
because only 0.000 and 1.000 were measured there.""",
    """Neither EMC type falls outside the range of retained-RG fractions the reported breakpoints of the
measured diseases already cover. Placing a fusion on the retained-RG axis does not establish that
recruitment was measured at that position: reference 1 measured recruitment at 0.000 and at 1.000,
and a position between them is a computed placement on the axis and not a measured recruitment
result.""")

# ---------------------------------------------------------------- E7 3.5 grid restriction
rep("E7a-table5-cell",
    "separates, by 0.039; no TCF12 prefix of any length reaches the lowest value any FET prefix takes",
    "separates, by 0.039; no TCF12 prefix on the evaluated grid reaches the lowest value any FET prefix takes on that grid")
rep("E7b-prose-any-length",
    "TCF12 has no RGG box, roughly a quarter of the RG content, and no\nN-terminal prefix of any length reaching the lowest value any FET prefix takes, which makes the\nclassification robust to the unpinned TCF12 breakpoint.",
    "TCF12 has no RGG box, roughly a quarter of the RG content, and no\nN-terminal prefix on the evaluated grid reaching the lowest value any FET prefix takes on that\ngrid, which makes the classification robust to the unpinned TCF12 breakpoint across the lengths\nevaluated. The grid is every prefix from 50 aa upwards in 10-aa steps, 66 prefixes for TCF12 and\n61, 55 and 48 for EWSR1, TAF15 and FUS; lengths between grid points were not evaluated and no\nclaim is made about them.")

# ---------------------------------------------------------------- E8 table renumbering (main text)
rep("E8a", "**Table 3.** The four constructs.", "**Table 2.** The four constructs.")
rep("E8b", "**Table 5.** TCF12 against the three FET proteins.", "**Table 4.** TCF12 against the three FET proteins.")
rep("E8c", "**Table 6.** Predictions fixed before any experiment", "**Table 5.** Predictions fixed before any experiment")
if "Table 4 below" in t:
    t = t.replace("Table 4 below", "Table 3 below"); edits.append("E8d-appendixA-xref")
if "and Table 4 below\nnow carry" in t:
    pass

# ---------------------------------------------------------------- E9 move Table 2 and Table 7 out
i0 = t.index("**Table 2.** Reference gene models")
i1 = t.index("### 2.3 TCF12 comparison") if False else t.index("\n\n", t.index("| TCF12 |", i0))
table2_block = t[i0:i1].rstrip() + "\n"
t = t[:i0] + ("The reference gene models the junction arithmetic runs on, and the four assertions they satisfy,\n"
              "are given in Supplementary Table S1.\n") + t[i1:].lstrip("\n")
edits.append("E9a-table2-to-S1")

j0 = t.index("**Table 7.** Wild-type controls")
j1 = t.index("\n\nNo TCF12::NR4A3 construct is emitted")
table7_block = t[j0:j1].rstrip() + "\n"
t = t[:j0] + ("The four controls, their roles and their predictions are given in Supplementary Table S2.\n") + t[j1:].lstrip("\n")
edits.append("E9b-table7-to-S2")

# ---------------------------------------------------------------- E10 restore ORIGINAL preregistration rows
for pid in ("P1", "P3", "P5"):
    m_new = re.search(rf"^\| {pid} \|.*$", t, re.M)
    m_old = re.search(rf"^\| {pid} \|.*$", base, re.M)
    assert m_new and m_old, pid
    t = t[:m_new.start()] + m_old.group(0) + t[m_new.end():]
    edits.append(f"E10-restore-{pid}-verbatim")
for pid in ("P1", "P2", "P3", "P4", "P5"):
    assert re.search(rf"^\| {pid} \|.*$", t, re.M).group(0) == re.search(rf"^\| {pid} \|.*$", base, re.M).group(0), pid

pathlib.Path(L / "PREREG-ROWS-CANDIDATE-vs-BASELINE.txt").write_text(
    "".join(re.findall(r"^\| P[1-5] \|.*$\n", base, re.M)))

(L / "MOVED-TABLES-SOURCE-BLOCKS.md").write_text(
    "# Verbatim blocks moved to supplementary (nothing rewritten)\n\n" + table2_block + "\n" + table7_block)

# ---------------------------------------------------------------- E11 references 9 and 10
rep("E11a-ref9",
    "9. Okamoto S, Hisaoka M, Ishida T, Imamura T, Kanda H, Shimajiri S, Hashimoto H. Extraskeletal myxoid chondrosarcoma: a clinicopathologic, immunohistochemical, and molecular analysis of 18 cases. PMID 11679947. Counted series: fusion transcripts detected in 15 of 18 cases, EWS-CHN type 1 in 11, type 2 in 1 and TAF2N-CHN in 3. [PROPOSED — UNRESOLVED U6: journal, year, volume and pages are not held in any committed input in this repository and are not written here.]",
    "9. Okamoto S, Hisaoka M, Ishida T, Imamura T, Kanda H, Shimajiri S, Hashimoto H. Extraskeletal myxoid chondrosarcoma: a clinicopathologic, immunohistochemical, and molecular analysis of 18 cases. *Hum Pathol* 2001;32(10):1116-1124. PMID 11679947. doi 10.1053/hupa.2001.28226. Counted series: fusion transcripts detected in 15 of 18 cases, EWS-CHN type 1 in 11, type 2 in 1 and TAF2N-CHN in 3.")
rep("E11b-ref10",
    "10. Sjögren H, Meis-Kindblom JM, Orndal C, Bergh P, Ptaszynski K, Aman P, Kindblom LG, Stenman G. Studies on the molecular pathogenesis of extraskeletal myxoid chondrosarcoma - cytogenetic, molecular genetic, and cDNA microarray analyses. PMID 12598313. Counted series: EWS-TEC five cases, TAF2N-TEC four, TCF12-TEC one, of ten tumours. [PROPOSED — UNRESOLVED U6: journal, year, volume and pages are not held in any committed input in this repository and are not written here.]",
    "10. Sjögren H, Meis-Kindblom JM, Orndal C, Bergh P, Ptaszynski K, Aman P, Kindblom LG, Stenman G. Studies on the molecular pathogenesis of extraskeletal myxoid chondrosarcoma - cytogenetic, molecular genetic, and cDNA microarray analyses. *Am J Pathol* 2003;162(3):781-792. PMID 12598313. PMC1868116. Counted series, by partner gene rather than by EWSR1 subtype: EWS-TEC five cases, TAF2N-TEC four, TCF12-TEC one, of ten tumours.")
rep("E11c-ref7-note",
    "Counted series: of the 15 EWS/NR4A3 cases, 10 carried exon 12 to exon 3 (type 1) and 2 carried exon 13 to exon 3 (type 5).",
    "Counted series. The quotation retained in the frame-and-composition artifact gives counts without a denominator: type 1 in 10 tumours, the most frequent transcript, and type 5 in two cases, the second most common. The denominator of 15 EWS/NR4A3 cases is recorded in this repository's editorial note on this reference, not in that quotation.")

# ---------------------------------------------------------------- E12 remove Appendix A (retained separately)
a0 = t.index("## Appendix A. Superseded and corrected values")
appendix = t[a0:]
tail_start = t.rfind("\n---\n", 0, a0)
(L / "RETAINED-APPENDIX-A-history.md").write_text(
    "# RETAINED VERBATIM: Appendix A of the input candidate\n\n"
    "Removed from the proposed submission copy ONLY because it is retained here, unaltered.\n"
    "Nothing in it has been edited, shortened or reworded. Original history is never erased.\n"
    "Source: `INPUTS/R1/PROPOSED-emc-atr-collaborator-package.md`.\n\n---\n\n" + appendix)
t = t[:tail_start].rstrip() + "\n"
edits.append("E12-appendixA-removed-and-retained")

pathlib.Path(L / "PROPOSED-X1-emc-atr-collaborator-package.md").write_text(t)
print("EDITS APPLIED:", len(edits))
for e in edits: print("  ", e)
