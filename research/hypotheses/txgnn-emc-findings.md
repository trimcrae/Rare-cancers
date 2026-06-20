# TxGNN on EMC — what the trained model actually predicts (and why it's a limitation finding)

We ran the **real** pretrained TxGNN foundation model (Huang et al., *A foundation model
for clinician-centered drug repurposing*, **Nat Med 2024**, doi:10.1038/s41591-024-03233-x;
`mims-harvard/TxGNN`) zero-shot on the EMC disease node and ranked all **7,957** drugs by
the model's *indication* score. Reproduce: `txgnn_predict.py` + `.github/workflows/txgnn-run.yml`;
raw output `txgnn-emc-predictions.json` (snapshot here; auto-refreshed on the `txgnn-cache`
branch). How TxGNN works is summarised in `METHODOLOGY.md §7`.

This is a genuine model output, **not** a hand-built heuristic — and the result is itself
the finding.

## Result: TxGNN diverges from mechanism and enumeration for EMC

**Top model picks** are dominated by lysosomal/metabolic-disease drugs with no EMC
mechanism — ORE-1001, asfotase alfa, the Gaucher enzyme-replacement therapies
(imiglucerase / alglucerase / taliglucerase / velaglucerase), mecasermin, miglustat, and
assorted phosphate/glutathione metabolites.

**Our mechanism- and enumeration-derived leads rank low** (of 7,957; higher percentile =
better):

| Drug | TxGNN rank | percentile | note |
|---|---:|---:|---|
| doxorubicin | 2017 | 74.7 | standard sarcoma chemo — our only above-median lead |
| masitinib | 3784 | 52.4 | ~median |
| imatinib | 5951 | 25.2 | **our T3 lead (real EMC response in a KIT-mutant patient)** |
| sunitinib | 6382 | 19.8 | **clinically active in EMC** |
| pazopanib | 6422 | 19.3 | **most active systemic class in EMC** |
| cabozantinib | 6400 | 19.6 | |
| trabectedin | 7158 | 10.0 | used in EMC |
| pioglitazone | 7725 | 2.9 | PPARγ axis |
| gemcitabine | 7750 | 2.6 | |

The drugs with the **strongest real-world EMC evidence** (pazopanib, sunitinib) and our
biomarker-supported T3 lead (imatinib) all land in the **bottom ~20–25%**, while the
model's top picks are clinically implausible for EMC. Two enumerated leads
(**fruquintinib, anlotinib**) are **absent from the 2023 knowledge graph** entirely.

## Why (honest interpretation)

EMC is **data-sparse in PrimeKG** (few disease–gene/treatment edges). TxGNN's value comes
from **zero-shot similarity transfer** — it borrows signal from the most graph-similar
diseases. For EMC those neighbours appear to be metabolic / lysosomal-storage disorders,
so predictions are pulled toward *their* drugs, **orthogonal to oncology mechanism**. This
is a clean, citable illustration of where KG foundation models break down: **ultra-rare
cancers with thin graph neighbourhoods.** It is not evidence that TxGNN is "wrong" in
general — only that, for EMC specifically, it neither corroborates our leads nor surfaces
plausible new ones.

## Caveats

- Released **`complex_disease`** pretrained checkpoint; a `disease_eval`/full-graph model
  could differ. Scores are logits (all our leads are negative = predicted *unlikely*
  indications; top hits are positive).
- KG currency: PrimeKG is ~2023, so newer agents (fruquintinib, anlotinib) are missing.
- Single disease node; grouped MONDO `12825_4392`.

## What we do with it (firewall)

- **No TxGNN hit is promoted** to the candidate catalog or the patient page — they fail
  the mechanism requirement (METHODOLOGY §1) and the firewall (§5).
- This belongs in the manuscript **Methods/Limitations** as a three-way *triangulation*:
  mechanism curation and target enumeration agree on oncology leads; the graph-ML
  foundation model diverges — and we report that honestly rather than cherry-picking.
