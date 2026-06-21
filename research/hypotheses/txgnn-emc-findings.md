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

## Sparsity stress-test — and why our first explanation was wrong

Our initial hypothesis was that EMC's **sparse** PrimeKG neighbourhood made zero-shot
similarity-transfer borrow from metabolic/lysosomal diseases, dragging oncology drugs down.
We tested it directly by re-running the same model on two **commoner** relatives
(`txgnn-relatives-comparison.json`):

| disease | our-drugs median percentile | top hit |
|---|---:|---|
| EMC | 21.0 | ORE-1001 |
| chondrosarcoma | 17.7 | ORE-1001 |
| soft-tissue sarcoma | 17.4 | ORE-1001 |

The relatives did **not** rescue the leads — they ranked our drugs *slightly worse* than EMC
did, with the **same** implausible top hits. **This refutes the sparsity explanation.** The
divergence is not specific to EMC's rarity; it is a general property of this released
checkpoint's *indication* ranking (across all three, only doxorubicin — a real sarcoma chemo —
ranks well; the targeted/anti-angiogenic agents rank low everywhere). We therefore report the
model as **non-corroboratory** for these leads, **without** ascribing a cause we cannot support.

## Caveats

- Released **`complex_disease`** pretrained checkpoint, which *holds out* drug–disease
  treatment edges — so none of the three diseases is a clean "data-rich" positive control, and
  a definitive mechanism would need the full-graph model. Scores are logits.
- KG currency: PrimeKG is ~2023, so newer agents (fruquintinib, anlotinib) are absent.
- One disease node each; EMC is grouped MONDO `12825_4392`.
- **Process note:** the sparsity claim was in an earlier draft and was *removed* after this
  stress-test contradicted it — an example of the verification catching an unsupported causal
  claim before submission.

## What we do with it (firewall)

- **No TxGNN hit is promoted** to the candidate catalog or the patient page — they fail
  the mechanism requirement (METHODOLOGY §1) and the firewall (§5).
- This belongs in the manuscript **Methods/Limitations** as a three-way *triangulation*:
  mechanism curation and target enumeration agree on oncology leads; the graph-ML
  foundation model diverges — and we report that honestly rather than cherry-picking.
