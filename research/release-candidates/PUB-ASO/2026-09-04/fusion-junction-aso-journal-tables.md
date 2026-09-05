<!-- GENERATED, DO NOT EDIT. Release interpretation corrected by build_data.py; canonical numeric source: aso_journal_tables.py -->

# Display items: fusion-junction ASO journal article

*Every value in the tables below is read from a committed artifact and none is typed by hand: the reagents from `fusion-junction-aso-sequences.csv`, the canonical machine-readable record, and the controls from `aso-control-oligos.json`, either directly or composed from their fields. The captions carry literature facts, each with its source named there. Every reagent named here is a 5-6-5 phosphorothioate gapmer. An oligonucleotide should be ordered from that file rather than transcribed from this page.*

**Table 1. The two reagents named for synthesis, with their parent-duplex label.** The parent-duplex column is the longest contiguous duplex a mature wild-type parent forms through the catalytic gap; neither reagent reaches the ten-base-pair criterion, so the length is printed rather than a pass mark. The test articles are the engineered constructs of Brenca et al. (PMID:31020999) — E-N for the *EWSR1* reagent and T-N* for the *TAF15* reagent; the two patient-derived models of Bangerter et al. (PMID:36316541) are reported at an NR4A3 exon-2 acceptor; correspondence to these reagents requires nucleotide-junction confirmation. ΔTm separates the fusion duplex from the more stable half of the design's own target window, which is a different parent from the duplex column's searched wild-type TFG. These are differences from the unmodified DNA:RNA model at 250 nM strand concentration. LNA and phosphorothioate effects are unmodelled, so these values are not validated predictions or bounds for the proposed modified reagents. Nothing here has been synthesised or tested, and no sequence may be administered to any person or animal.

| seam | reagent | margin | WT gap duplex (bp) | Model ΔTm (°C) |
|---|---|---:|---|---:|
| *EWSR1* e12::*NR4A3* e3 | 5′-GGGCATATCATCAAAC-3′ | 3 | 8 bp, wild-type *TFG* | 26.6 |
| *TAF15* e6::*NR4A3* e3 | 5′-GGGCATATCTTGTGTG-3′ | 3 | 9 bp, wild-type *TFG* | 36.0 |

**Table 2. The two control oligonucleotides, each screened as its reagent was.** Each is a dinucleotide-preserving scramble of the reagent it controls, matching it in length, first and last base, base composition and dinucleotide counts while spanning no junction, and each cleared the same mature-parent screen the reagent did. The Controls section above explains why that screening step makes a scramble a control.

| control | sequence | scramble of | WT gap duplex (bp) |
|---|---|---|---|
| control-1 | 5′-GGGCATCAACATAATC-3′ | the EWSR1 e12 :: NR4A3 e3 reagent | 6 bp, wild-type *TAF15* |
| control-2 | 5′-GTATGTCATTGGCTGG-3′ | the TAF15 e6 :: NR4A3 e3 reagent | 7 bp, wild-type *EWSR1* |
