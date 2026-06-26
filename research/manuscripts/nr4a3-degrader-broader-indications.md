> **Role:** the **indication stack** for the NR4A3-degrader paper — see the positioning decision in
> [`nr4a3-degrader-paper-positioning.md`](./nr4a3-degrader-paper-positioning.md). The degrader paper
> leads with NR4A3 (target-centric); EMC is the lead clinical application among several **NR4A3-selective**
> indications.

# Beyond EMC: what else could a *selective* NR4A3 degrader treat?

**Purpose (manuscript motivation section).** EMC is ultra-rare, which weakens the commercial case for
*making* the molecule. The degrader we design **must be NR4A3-selective** — it has to spare NR4A1 and
NR4A2 to avoid their on-target toxicities (NR4A1/NR4A3 loss → leukaemia; NR4A1/Nurr1 loss →
dopaminergic/neuronal liabilities). So the relevant question is **not** "where is *any* NR4A degrader
useful" but specifically **"what else benefits from removing NR4A3 while sparing NR4A1/2."** The answer
is what justifies the broadened framing — and it is coherent, because every lead indication below pulls
in the *same* selectivity direction as EMC.

## Framing: the indication must want NR4A3 *down* AND NR4A1/2 *spared*
A degrader lowers NR4A3 protein. It helps only where NR4A3 *specifically* is pathogenic, and it is safe
only if NR4A1/2 are spared. NR4A biology is **paradoxical and tissue-specific** (Safe & Karki, *Mol
Cancer Res* 2021): NR4A3 is oncogenic in a few contexts but **tumour-suppressive in many**, so the
indication list is short and must be curated, not assumed.

## A. Lead indications for an NR4A3-SELECTIVE degrader (coherent with EMC)
These all want NR4A3 removed and NR4A1/2 spared — the *same* molecule we design for EMC. The warhead
binds the NR4A3 LBD, which is present both in the EMC fusion **and** in over-expressed wild-type NR4A3,
so one selective degrader covers all three.

1. **Extraskeletal myxoid chondrosarcoma (EMC) — lead / proof-of-concept.** EWSR1::NR4A3 (or
   TAF15::NR4A3) fusion driver; the fusion retains a near-intact NR4A3 LBD. Clean single-driver biology.

2. **Acinic cell carcinoma (AciCC) of the salivary glands — the key second indication.** AciCC is driven
   by **NR4A3 over-expression via enhancer hijacking** — a recurrent t(4;9)(q13;q31) translocates SCPP
   (e.g. *HTN3*) secretory-gland enhancers upstream of *NR4A3*, switching it on as the oncogenic driver
   (Haller et al., *Nat Commun* 2019); NR4A3 then cooperates with MYB (Haller et al. 2020). NR4A3 is the
   defining diagnostic marker and the driver. A **selective** degrader (remove over-expressed NR4A3,
   spare NR4A1/2) applies directly, and AciCC is **substantially more common than EMC** (a leading
   salivary-gland carcinoma, prominent in younger patients) — materially enlarging the addressable
   population for the *same selective drug*.

3. **Other NR4A3-rearranged sarcomas (direct extension).** The EMC fusion-variant spectrum (EWSR1 most
   common, TAF15 second, rarer partners) all converge on an NR4A3-fusion TF. *(Exact partner list to
   verify against a current EMC cytogenetics review before submission.)*

**Mechanistic aptness:** NR4A3 is constitutively active and its oncogenic output scales with protein
level, so in both the fusion (EMC) and over-expression (AciCC) settings, *lowering NR4A3 lowers
oncogenic activity* — degradation is the right modality, and selectivity is what makes it safe.

## B. Contingency only — value IF the degrader turns out NON-selective (pan-NR4A)
These do **not** motivate the selective EMC drug; they would only become relevant if the designed
warhead/pocket proves non-selective and we instead obtain a **pan-NR4A** degrader. Recorded as
optionality, explicitly *not* as justification for the selective program.

- **Immuno-oncology — reversing T-cell exhaustion.** NR4A1/2/3 drive CD8⁺ T-cell exhaustion, but the
  effect is **complementary across all three**: NR4A *triple* knockout is required for the full benefit
  (single/double KO underperform), and NR4A-triple-KO CAR-T cells resist exhaustion with superior
  tumour control (Chen et al., *Nature* 2019; Odagiu/CAR-T persistence work 2024). **This needs a
  pan-NR4A degrader — the opposite of the EMC requirement — so it belongs here, not in the lead set.**
  (A reciprocal BLIMP1↔NR4A3 axis in CAR-T stemness has an NR4A3-specific angle, but the dominant,
  reproducible result is triple-NR4A.)
- **Solid tumours with oncogenic NR4A1/NR4A2.** Pro-oncogenic NR4A1/2 in pancreatic/lung/breast/
  colorectal (Safe & Karki 2021) — a *non-selective* degrader could help, again a pan-NR4A play.

## C. Where a selective NR4A3 degrader would be HARMFUL (contraindications)
- **Myeloid/lymphoid malignancies (AML, some lymphomas):** NR4A1 and NR4A3 are **tumour suppressors** in
  the blood lineage — combined *Nr4a1/Nr4a3* loss causes AML and NR4A is low in blasts (Mullican et al.,
  *Nat Med* 2007). The goal there is to *raise* NR4A; a degrader is **leukemogenic**. (This is also the
  toxicity that mandates NR4A1-sparing selectivity for systemic dosing.)
- **Tumour-suppressor solid-tumour contexts:** NR4A3 is tumour-suppressive in hepatocellular carcinoma
  (low NR4A3 → poor prognosis), breast cancer and lymphoma (NR4A3 over-expression is pro-apoptotic), and
  bladder cancer (Safe & Karki 2021; HCC: IJBS 2024). A degrader is contraindicated there.

## One-paragraph version for the manuscript
*"The degrader is designed to be NR4A3-selective, sparing NR4A1/2 to avoid their on-target toxicities
(notably the leukaemia risk of combined NR4A1/NR4A3 loss). That same selective agent addresses more than
EMC: it targets the NR4A3 LBD shared by the EMC fusion and by wild-type NR4A3 over-expressed in acinic
cell carcinoma of the salivary glands — a substantially more common cancer in which NR4A3, switched on by
enhancer hijacking, is the oncogenic driver (Haller et al., Nat Commun 2019) — as well as the broader
NR4A3-rearranged sarcoma spectrum. We explicitly do not invoke NR4A's role in T-cell exhaustion as
motivation, because that requires pan-NR4A degradation (NR4A triple-knockout; Chen et al., Nature 2019),
the opposite of the selectivity EMC demands; it is noted only as optional value should the agent prove
non-selective. NR4A3 is tumour-suppressive in several other tissues (AML, HCC, breast/lymphoma), which
bounds the indication set and reinforces the selectivity requirement."*

## References (verified against primary sources)
- Haller F, et al. *Enhancer hijacking activates oncogenic transcription factor NR4A3 in acinic cell
  carcinomas of the salivary glands.* **Nat Commun** 10:368 (2019). PMC6341107 / PubMed 30664630.
- Haller F, et al. *Oncogenic orphan nuclear receptor NR4A3 interacts and cooperates with MYB in acinic
  cell carcinoma.* (PMC7565926, 2020). *(locator to confirm.)*
- Chen J, et al. *NR4A transcription factors limit CAR T cell function in solid tumours.* **Nature**
  567:530–534 (2019). (triple-NR4A requirement.)
- Mullican SE, et al. *Abrogation of nuclear receptors Nr4a3 and Nr4a1 leads to development of acute
  myeloid leukemia.* **Nat Med** 13:730–735 (2007). PubMed 17515897.
- Safe S, Karki K. *The Paradoxical Roles of Orphan Nuclear Receptor 4A (NR4A) in Cancer.* **Mol Cancer
  Res** 19(2):180–191 (2021). PMC7864866.
- EMC NR4A3 fusion-variant spectrum (EWSR1/TAF15/…): *attach a current EMC molecular-pathology review
  before submission.*

*Medical-integrity note: sourced claims; locators flagged "to confirm" must be verified against the
primary literature before submission, and no clinical claim should outrun the cited evidence.*
