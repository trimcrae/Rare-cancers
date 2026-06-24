# Fact-check & replication log — repurposing-hypotheses.md

> **QA / FACT-CHECK LOG (not a manuscript)** for [`repurposing-hypotheses.md`](./repurposing-hypotheses.md).
> Active manuscript: [`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md). Folder map: [`README.md`](./README.md).

Reviewer-grade verification trail. "Corpus" = the project's PubMed metadata index used to
build the catalogue (abstracts + identifiers). ✓ = verified; ⚠ = needs full-text/online
confirmation a hostile reviewer could demand; ✗ = found wrong and fixed.

## Replication (re-run, expect no drift)
- `node research/hypotheses/build-candidates.mjs` → `candidates.json` byte-identical to committed. ✓
- Figures are inline Markdown tables + a Mermaid diagram (no SVG); they render on GitHub.
- `validate.mjs`, `validate-research.mjs`, `smoke-render.mjs` → all PASS. ✓
- TxGNN outputs regenerate via CI (`txgnn-run.yml`); EMC ranks + stress-test reproduced. ✓

## Reference identifiers (all 16)
- **12 EMC references cross-checked vs the PubMed corpus by PMID/PMCID → title, DOI, year: all ✓**
  (Davis 2017, Urbini 2018, Jennings 2021, Huang SC 2023, Kim 2016, Higuchi 2023, Bangerter 2023,
  Iwata 2025, O'Sullivan Coyne 2022, Masunaga 2025, Remiszewski 2025, Giner 2023).
- **4 non-EMC references confirmed via Crossref in CI** (`verify-refs.yml`): titles + journals
  match exactly — TxGNN (Nat Med 2024), KEYNOTE-942 (The Lancet 2024), LNP review (Exp & Mol
  Med 2023), DGIdb 4.0 (Nucleic Acids Research). ✓ Note: Crossref dates DGIdb **2020**
  (online-first); we cite **2021** (the NAR Database D1 issue year) — both are standard.
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
| Venetoclax/carfilzomib/doxorubicin sensitivity + synergy in 2 ex vivo models | Bangerter 2023 | ✓ **full text verified via CI (NCBI efetch, `verify-refs.yml`)**: "Drug sensitivities for carfilzomib, doxorubicin and venetoclax were validated … for both cell models"; synergies carfilzomib+venetoclax and carfilzomib+doxorubicin. Resolves the earlier abstract-only gap. |
| Anti-angiogenic TKIs (pazopanib, sunitinib) most consistently active class | Remiszewski 2025 (review) | ⚠ secondary, but **primary EMC reports exist to cite** (found via CI search): e.g. PMID 41323055 (2025, metastatic-EMC antiangiogenic response), 36910639 (2023, antiangiogenic + PD-1 in metastatic disease) |

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
