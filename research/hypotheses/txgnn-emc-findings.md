---
id: DOC-TXGNN-EMC-FINDINGS
title: TxGNN on EMC — what the trained model actually predicts (and why it's a limitation finding)
level: L5
kind: memo
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `memo` from its location under research/hypotheses/.
audience: [maintainers, autonomous research agents]
date: 2026-08-05
last_verified: 2026-08-10
_backfilled: true
---

> ⛔ **CORRECTED 2026-08-10 — THREE OF THE RANKS BELOW WERE A DIFFERENT MOLECULE.**
> `txgnn_predict.relevant_ranks` matched a query to the ranking by **substring** against a
> descending-sorted list, so it returned the highest-scoring compound whose name *contained* the
> query. `doxorubicin` resolved to **13-deoxydoxorubicin** (EMC, soft-tissue sarcoma) and to
> **Zoptarelin doxorubicin** (chondrosarcoma), `apatinib` to **Lapatinib**, `ifosfamide` to
> **Palifosfamide**. The headline of the original version of this memo — "doxorubicin 2017 / 74.7 —
> our only above-median lead" — named a compound the model did not rank against this query.
> The matcher is fixed; the artifacts below **predate the fix and have not been regenerated**,
> because only the top 100 (EMC) and top 15 (each comparison node) of the 7,957-drug ranking were
> ever committed, so the true ranks of those three agents are **not recoverable without re-running
> the model**. They are reported as unknown rather than estimated. Exact-match re-derivation:
> [`txgnn_exact_match_reanalysis.py`](./txgnn_exact_match_reanalysis.py) →
> `txgnn-exact-match-reanalysis.json`.
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

**Our mechanism- and enumeration-derived leads rank low.** 28 of the 33 queried agents resolved
to themselves; those are the only rows quotable (of 7,957; higher percentile = better):

| Drug | TxGNN rank | percentile | note |
|---|---:|---:|---|
| masitinib | 3784 | 52.4 | the best EXACTLY-matched agent, and it is ~median |
| imatinib | 5951 | 25.2 | **our EMC-case lead (response in a KIT-mutant patient)** |
| sunitinib | 6382 | 19.8 | **clinically active in EMC** |
| cabozantinib | 6400 | 19.6 | |
| pazopanib | 6422 | 19.3 | **most active systemic class in EMC** |
| trabectedin | 7158 | 10.0 | used in EMC |
| pioglitazone | 7725 | 2.9 | PPARγ axis |
| gemcitabine | 7750 | 2.6 | |
| doxorubicin | — | — | ⛔ **UNKNOWN.** The substring matcher returned 13-deoxydoxorubicin (2017 / 74.7); doxorubicin's own rank needs a re-run |
| apatinib | — | — | ⛔ **UNKNOWN.** Returned Lapatinib (6693 / 15.9) |
| ifosfamide | — | — | ⛔ **UNKNOWN.** Returned Palifosfamide (5531 / 30.5) |

The drugs with the **strongest real-world EMC evidence** (pazopanib, sunitinib) and our
biomarker-supported EMC-case lead (imatinib) all land in the **bottom ~20–25%**, while the
model's top picks are clinically implausible for EMC. Two enumerated leads
(**fruquintinib, anlotinib**) are **absent from the ~2023 knowledge graph** entirely, so they are
excluded from every summary statistic rather than counted as low ranks.

## Sparsity stress-test — and why our first explanation was wrong

Our initial hypothesis was that EMC's **sparse** PrimeKG neighbourhood made zero-shot
similarity-transfer borrow from metabolic/lysosomal diseases, dragging oncology drugs down.
We tested it directly by re-running the same model on two **commoner** relatives
(`txgnn-relatives-comparison.json`):

| disease node | median percentile, 28 exactly-matched agents | IQR | top-ranked compound |
|---|---:|---|---|
| EMC | 20.9 | 18.2–24.0 | ORE-1001 |
| chondrosarcoma | 17.6 | 12.8–25.0 | ORE-1001 |
| soft-tissue sarcoma | 17.0 | 15.0–18.9 | ORE-1001 |

*(Superseded, retained: **21.0 / 17.7 / 17.4**, computed over 31 rows of which three were a
different molecule and using the upper-middle order statistic rather than a median. Each substring
percentile is an **upper bound** on the agent's own — the agent's name contains its own query, so
the matcher returns something scoring at least as high — hence so were those three medians.)*

The comparators did **not** rescue the leads — the same agents ranked *slightly worse* at both
than at the EMC node, the same compound (ORE-1001) ranked first at all three, and 5 of each top 15
are shared. **This is not consistent with the sparsity explanation**, and pazopanib and sunitinib
sit in the bottom quintile at all three nodes. ⚠ **It does not settle the cause**: the two
comparators are commoner *in the population*, and nothing here measures their knowledge-graph node
degree or indication count, which is the quantity the argument needs. We therefore report the
model as **non-corroboratory** for these leads, **without** ascribing a cause we cannot support.
⚠ *Superseded, retained: "across all three, only doxorubicin — a real sarcoma chemo — ranks well",
which rested on the mis-resolved match above; the best exactly-matched agent at every node is
masitinib.*

## Caveats

- Released **`complex_disease`** pretrained checkpoint, which *holds out* drug–disease
  treatment edges — so none of the three diseases is a clean "data-rich" positive control, and
  a definitive mechanism would need the full-graph model. Scores are logits.
- KG currency: PrimeKG is ~2023, so newer agents (fruquintinib, anlotinib) are absent.
- One disease node each; EMC is grouped MONDO `12825_4392`.
- ⚠ **The two comparators are not EMC's relatives, and were selected by node availability.** The
  WHO places EMC among tumours of **uncertain differentiation**; it is not a cartilaginous tumour
  and is genetically unrelated to conventional chondrosarcoma, so `chondrosarcoma (disease)` is a
  commoner comparator node that shares EMC's historical name, not a close relative. A genuinely
  close comparator would be another FET-fusion sarcoma. *(Superseded, retained: "two data-rich
  relatives", in this file and in `txgnn_predict.py`.)*
- **Process note:** the sparsity claim was in an earlier draft and was *removed* after this
  stress-test contradicted it — an example of the verification catching an unsupported causal
  claim before submission.

## What we do with it (firewall)

- **No TxGNN hit is promoted** to the candidate catalogue or the clinical registry — they fail
  the mechanism requirement (METHODOLOGY §1) and the firewall (§5).
- This belongs in the manuscript **Methods/Limitations** as a three-way *triangulation*:
  mechanism curation and target enumeration agree on oncology leads; the graph-ML
  foundation model diverges — and we report that honestly rather than cherry-picking.
