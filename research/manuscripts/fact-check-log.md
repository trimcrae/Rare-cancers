# Fact-check & replication log — repurposing-hypotheses.md

Reviewer-grade verification trail. "Corpus" = the project's PubMed metadata index used to
build the catalogue (abstracts + identifiers). ✓ = verified; ⚠ = needs full-text/online
confirmation a hostile reviewer could demand; ✗ = found wrong and fixed.

## Replication (re-run, expect no drift)
- `node research/hypotheses/build-candidates.mjs` → `candidates.json` byte-identical to committed. ✓
- `node research/manuscripts/figures/make-figures.mjs` → both SVGs byte-identical. ✓
- `validate.mjs`, `validate-research.mjs`, `smoke-render.mjs` → all PASS. ✓
- TxGNN outputs regenerate via CI (`txgnn-run.yml`); EMC ranks + stress-test reproduced. ✓

## Reference identifiers (all 16)
- **12 EMC references cross-checked vs the PubMed corpus by PMID/PMCID → title, DOI, year: all ✓**
  (Davis 2017, Urbini 2018, Jennings 2021, Huang SC 2023, Kim 2016, Higuchi 2023, Bangerter 2023,
  Iwata 2025, O'Sullivan Coyne 2022, Masunaga 2025, Remiszewski 2025, Giner 2023).
- 4 non-EMC references verified via earlier web search / curated map, ⚠ confirm at submission:
  TxGNN/Huang K 2024 (doi 10.1038/s41591-024-03233-x; PMID 39148855); KEYNOTE-942/Weber 2024
  (doi 10.1016/S0140-6736(23)02268-7; PMID 38246194); LNP review 2023 (PMC10618257); DGIdb /
  Freshour 2021 (doi 10.1093/nar/gkaa1084).
- Author attributions fixed earlier: Kim 2016 (not "Yoshimura"); Huang SC 2023 (not "Warmke"). ✗→✓

## Key factual claims
| Claim (manuscript) | Source | Status |
|---|---|---|
| *NR4A3* fusion, EWSR1::NR4A3 most common; TAF15::NR4A3 less common | Remiszewski 2025; Huang SC 2023 | ✓ |
| Fusion drives transcription via chromatin modification | Kim 2016 (TFG-TEC β-enolase) | ✓ |
| No recurrent actionable mutations on NGS | Davis 2017 | ✓ |
| Activating *KIT* mutation rare: 1/20 (Urbini); 2/48 ≈4% (Huang SC) | Urbini 2018; Huang SC 2023 | ✓ (exact fractions) |
| Imatinib case: *KIT* exon-11 c.1669T>G, 3 yr stable disease | Jennings 2021 | ✓ (verbatim) |
| CD117/KIT IHC positivity ≈53% and ≈84% (n=31) — variable | Huang SC 2023; Giner 2023 | ✓ (range, not a single number) |
| CDK4 IHC 100%; CDKN2A/2B copy loss | Giner 2023; Davis 2017 | ✓ |
| Zaltoprofen inhibits EMC growth **in vivo** via PPARγ | Higuchi 2023 | ✓ ("mouse model of EMC", tumour-growth inhibition) |
| Iwata model screen hits: brigatinib, panobinostat, romidepsin | Iwata 2025 | ✓ (221-drug HTS, named in abstract) |
| Venetoclax/carfilzomib/doxorubicin sensitivity + synergy in 2 ex vivo models | Bangerter 2023 | ⚠ abstract confirms a functional screen with synergies but does **not name** these drugs — identities rest on full text/figures; confirm before submission |
| Anti-angiogenic TKIs (pazopanib, sunitinib) most consistently active class | Remiszewski 2025 (review) | ⚠ secondary source; cite primary EMC reports at submission |

## TxGNN numbers (vs `txgnn-emc-predictions.json` / `txgnn-relatives-comparison.json`)
- pazopanib #6422 (19.3 pct), sunitinib #6382 (19.8), imatinib #5951 (25.2), of 7,957. ✓
- "bottom quartile" reserved for pazopanib/sunitinib (≈19–20th pct, i.e. rank > 5968);
  imatinib at the 25th pct is **just above** that line — text corrected to "19th–25th percentile". ✗→✓
- Sparsity stress-test medians: EMC 21.0, chondrosarcoma 17.7, soft-tissue sarcoma 17.4 pct. ✓
- **Sparsity *causal* claim ✗→removed**: relatives ranked the leads no better (worse), refuting
  "EMC's sparse neighbourhood drives the divergence". Corrected in abstract, §2, §5, METHODOLOGY,
  findings doc.

## Open items for the human authors (cannot close offline)
- Confirm the Bangerter venetoclax/carfilzomib/doxorubicin identities against the paper's figures.
- Cite primary pazopanib/sunitinib EMC reports (not only the review) for the "most active class".
- Re-confirm "untried in EMC" with a dated database search.
- Confirm the 4 non-corpus DOIs/PMIDs resolve and complete all references to journal style.
