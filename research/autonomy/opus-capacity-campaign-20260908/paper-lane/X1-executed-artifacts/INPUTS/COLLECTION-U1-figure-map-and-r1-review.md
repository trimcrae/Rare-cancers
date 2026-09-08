# U1 — collection: figure panel map AND the independent review of R1's proposal

⛔ **Nothing applied.** Both deliverables are reviewable candidates; shared integration remains the
**scientific coordinator's** decision.

| item | measured |
|---|---|
| child | `af3a14e566b943e5e` |
| original JSONL | **2,024,627 B** |
| model strings | **`claude-opus-5` only** |
| tool pairs | **24** (self-reported 21) — **21 of a 35-call budget**, ~8 minutes of 30 |
| shared writes | **none**; porcelain empty at start and end |
| scope | original figure contract **plus** the in-flight amendment — **one child, no duplicate reviewer, no re-inspection** |

## ⭐ The finding that matters: four R1 results have NO figure support

The figure renders **177, never 176** — 1 + 174 + 2 = 177 = 59x3, `residues 265 to 323` = 59, and
793 = 3x264+1. So **R1's "177 spanned, 176 supplied by NR4A3" is correct**: two different quantities,
not a conflict.

But **four of R1's results are not in the figure at all**: (1) the frame rule *as a rule* — Panel C
shows one instance, never the mod-3 statement; (2) the phase-1 donor set; (3) **the symmetric sweep —
neither 0.439 nor 0.400 nor 0.039 is rendered, and TCF12 appears nowhere in any panel**; (4) the
margin 13. ⭐ **Citing Figure 1 for any of these would be false.**

**Parent check of U1's own named next step, which it did not run:** `grep -c "Figure 1"` returns **0**
in the committed manuscript **and 0** in R1's proposed manuscript, and none of `0.439`, `0.400`,
`TCF12` or `13 residues` occurs on a line mentioning Figure 1. **The cross-reference trap does not
exist in either document** — U1's concern was sound and is now closed, cheaply, as it suggested.

## The panel map

Three panels. **A** protein bars on a residue axis (EWSR1 30 RG, TAF15 31 RG, NR4A3 2 RG, C166 on
NR4A3) with seven fusions and their retained-RG counts. **B** a retained-RG-fraction axis with the
hatched *"position on this axis not determinable"* band and the 0.000-0.267 ATF1 span. **C** the seam
schematic — *"NR4A3 exon 2, 174 nt, untranslated in NR4A3"*, *"one nucleotide donated by EWSR1"*,
**"59 codons, 177 nt, no internal stop codon"**. ⭐ **Panel C never prints "type 2"** — a scope clause
is needed in any caption.

**Absent, not illegible:** the figure has **no key at all** — the dashed boxes and internal ticks are
unlabelled. U1 flagged its own reading of them (RG dipeptides, RGG regions) as **inference, not
pixels**. Everything else rests on pixels; nothing rests on the generator.

## The R1 review

**M1/M3/M6-M14 SUPPORTED** against `type2_seam`, `frame_rule`, `symmetric_prefix_sweep`,
`taf15_zero_rg_margin`, `recruitment_axis_rows` and the test; **M2/M4/M5/M15 PARTLY SUPPORTED**
(attribution nits). **D5 sound; D2/D3 sound with a check** — D3 now unblocked by U1's caption;
**D1/D6/D7 premature**; ⭐ **D4's restraint upheld** — the predictions are preregistration-shaped, with
`registered_predictions` confirmed at `emc-fet-construct-designs.json:1621`.

**Two of R1's eight unknowns were resolvable from committed inputs R1 never opened:** U2 (the PNG) and
**U6 for Sjögren 2003 — Am J Pathol 2003;162(3):781-92, PMC1868116, committed at
`research/autonomy/hardening-state/PUB-FUSION-PARTNER.json:88`**. Okamoto 2001 genuinely has none.

**Recommended integration scope:** Tier 1 the mechanical corrections + D5; Tier 2 D3 with U1's caption
**and the four unsupported cross-references withheld**, plus reference 10; Tier 3 D1/D4/D6/D7 and the
remaining unknowns.

**Bounds held:** no figure regenerated, no science or gate rerun, no network, no census, no whole-paper
review, no shared edit, no git write, nothing applied, nothing deleted.
