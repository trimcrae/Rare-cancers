# Verbatim blocks moved to supplementary (nothing rewritten)

**Table 2.** Reference gene models, from the UniProt and Ensembl records retrieved into the input cache [8].

| gene | transcript | protein | transcript / coding exons | Ensembl matches UniProt |
|---|---|---|---|---|
| EWSR1 | ENST00000397938 | 656 aa | 17 / 17 | yes |
| TAF15 | canonical | 592 aa | 16 / 16 | yes |
| FUS | canonical | 526 aa | 15 / 15 | yes |
| NR4A3 | ENST00000395097 | 626 aa | 8 / 6, exons 1-2 non-coding | yes |
| TCF12 | canonical | 706 aa | 21 / 19 | no; UniProt Q99081 is 682 aa |

**Table 7.** Wild-type controls and their predictions. Full-length sequences are in the artifact
under `wild_type_controls`.

| control | role | prediction |
|---|---|---|
| GFP-EWSR1, full length | fast-recruitment anchor, already held by any laboratory running the assay | rapid recruitment, as published. Failure to reproduce it makes nothing else in the run interpretable |
| GFP-TAF15, full length | wild-type anchor for the TAF15::NR4A3 arm | rapid recruitment, as TAF15 carries its own C-terminal RGG region. Not previously reported in this assay, so a prediction rather than a reproduction |
| GFP-NR4A3, full length | partner-alone control, the EMC analogue of reference 1's GFP-FLI1 control | no accumulation. Recruitment of NR4A3 alone would remove the attribution of the fusion's recruitment to the FET moiety |
| GFP-TCF12, full length | partner-alone anchor for the P5 arm | no accumulation, TCF12 being non-FET by section 3.5 |
