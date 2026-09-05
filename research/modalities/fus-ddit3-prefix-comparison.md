---
id: DOC-FUS-DDIT3-PREFIX-COMPARISON
title: Conditional native FUS prefixes in sourced FUS::DDIT3 variants
level: L4
kind: memo
status: generated
generator: research/modalities/fus_ddit3_prefix_comparison.py
purpose: "Compare the three sourced native FUS prefixes with the existing zero-RG rule."
scope: "Conditional secondary sequence arithmetic; no complete fusion or mechanism validation."
audience: [maintainers, autonomous research agents]
date: 2026-09-05
last_verified: 2026-09-05
---

# Conditional native FUS prefix comparison

**All prefixes meet the zero-RG rule: no.** The table reports exact native-prefix arithmetic under the assumption below.

Assume the reported literature exon ranks correspond to committed ENST00000254108 and that FUS is retained from its native start through the end of the named exon. This correspondence has not been established by accession-version sequence alignment.

The [committed primary-junction record](../autonomy/evidence-fus-ddit3-2026-09-05/primary-junctions.json) supplies every type and exon rank, from the indexed primary abstract of Bode-Lesniewska et al. (2007; PMID 17647282; DOI 10.1002/gcc.20478). No new retrieval was performed.

For each row, sum `coding_nt_in_exon` from exon 1 through the sourced retained exon; compare that sum with `cumulative_coding_nt_through_exon` and `cdna_end_exclusive - utr5_len`. Divide by three: the quotient determines the only protein slice counted, and the remainder is untranslated here. Scan every adjacent pair in that slice, including overlapping search windows; both residues must be inside it. Positions are 1-based, inclusive; lengths are nt or amino-acid residues as labeled. Three source variants are evaluated; there are no biological replicates or statistical uncertainty estimates. Uncertainty concerns mapping and the unresolved junction.

| Type | FUS exon / DDIT3 exon | Coding-nt sum = stored cumulative | cDNA end - UTR (nt) | Division by 3 | Native terminal residue | Internal RG / native total | Exact fraction | Prefix RG = 0 |
|---|---|---|---|---|---|---|---|---|
| II | 5 / 2 | 13 + 25 + 152 + 145 + 188 = 523 | 599 - 76 = 523 | 174 aa + 1 nt | G | 0 / 24 | 0 | yes |
| I | 7 / 2 | 13 + 25 + 152 + 145 + 188 + 241 + 35 = 799 | 875 - 76 = 799 | 266 aa + 1 nt | G | 8 / 24 | 1/3 | no |
| III | 8 / 2 | 13 + 25 + 152 + 145 + 188 + 241 + 35 + 33 = 832 | 908 - 76 = 832 | 277 aa + 1 nt | S | 8 / 24 | 1/3 | no |

- Type II internal RG positions: none. First unresolved residue position: 175.
- Type I internal RG positions: 213-214, 216-217, 218-219, 242-243, 244-245, 248-249, 251-252, 259-260. First unresolved residue position: 267.
- Type III internal RG positions: 213-214, 216-217, 218-219, 242-243, 244-245, 248-249, 251-252, 259-260. First unresolved residue position: 278.

Native FUS contains 24 RG dipeptides. The JSON enumerates all native pairs and every retained prefix sequence. The frozen first RG begins at 213 and `rgg_free_ceiling` is 212; all three rows agree with both reference checks. The ceiling is only a consistency reference: an R at the last complete position cannot count as an internal RG without its G. The census and its `rg_dipeptides_retained == 0` precondition are unchanged.

The cache, committed Ensembl/UniProt lengths and census length agree at 526 aa. The committed identity flag, FUS model self-checks and aggregate flag are true. All-exon coding length is 1581 nt, consistent with the protein plus one terminal stop codon. These stored identity/translation assertions were checked for presence and success; this run did not repeat alignment or translation.

Each row leaves one native nucleotide in a partial codon; its amino acid is unresolved. None of these complete prefixes ends in R, so no RG can start at its last complete residue and cross the boundary. RGs involving the unresolved codon or later sequence remain unassessed; no junction residue or DDIT3 sequence is reconstructed.

- Exploratory secondary sequence arithmetic on three sourced exon-level variants; not experimental or biological validation.
- No fusion nucleotide sequence is supplied. Junction codons, junction residues, DDIT3 sequence and the whole-fusion RG count remain unresolved.
- A zero native-prefix RG count does not prove zero RG in a whole fusion. A positive internal prefix count persists regardless of the unresolved junction under the explicit mapping assumption.
- The separate ATM mechanism experiment's exact FUS::CHOP construct/variant is not established by this input; these rows do not validate a mechanism positive control.
- No ATM mechanism, ATR response, safety, efficacy or clinical-stratification conclusion follows. The existing census precondition and acceptance rule are unchanged.

Reproduce with the configured Python executable and `research/modalities/fus_ddit3_prefix_comparison.py`; add `--check` to compare both outputs without writing. Behavioral tests are in `tests/test_fus_ddit3_prefix_comparison.py`. Exact input paths and SHA256 hashes are recorded in [the deterministic JSON](fus-ddit3-prefix-comparison.json). Stop condition: these conditional rows, this note and arithmetic/boundary tests; mapping alignment and identifying the ATM experiment construct are separate work.
