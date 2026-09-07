---
id: DOC-ATLAS-NORMAL-CONTEXT-INDEPENDENT-20260906
title: Independent fixed-panel HPA source verification
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Verify descriptive normal-context records against original HPA bytes.
scope: Twelve genes, tissue IHC, cell-based ICC/IF, RNA block provenance and source licensing.
audience: [maintainers, autonomous research agents]
---

Pass: no material parsing or source-interpretation repair is required. All12 XML/JSON gene/Ensembl identities, summaries, categorical reliability and reliability descriptions, ICC/IF locations, antibody fields and selected RNA annotations match the roster. The independent checker imports no worker code and applies no clinical-risk classifier.

All1,054 normal tissue/cell records reproduce directly from XML, including695 not-detected,112low,173medium and74high calls. All1,092 RNA tissue/block records reproduce, preserving source, assay type, organ, every level attribute and its original units/value. These are source records, not independently sampled subjects or new measurements. Exact source-file hashes match the worker manifest;2,242 row/field checks pass in addition to identity, assay and documentation assertions.

Named limitations are supported by the exact source:

- SSTR2 and FAP tissue-IHC reliability is uncertain. SSTR2's normal IHC includes brain while ICC/IF reports cytosol and nucleoplasm. FAP's missing ICC/IF block is not a membrane-absence result.
- GPC3 and CHRNA6 have no tissueExpression block and no IHC cell rows in these XML snapshots. CHRNA6 also lacks a cellExpression block. Missing evidence is not absence of normal protein and is not an automatic global research blocker.
- ALPP's ICC/IF summary explicitly warns about antibodies targeting proteins from multiple genes. Its placental trophoblast tissue summary remains visible; no ALPP-specific surface confirmation follows.
- CSPG4 normal IHC describes ubiquitous granular cytoplasmic expression, whereas its separate ICC/IF annotation is plasma membrane. Its categorical IHC reliability is approved, but the separate description states low consistency between staining and RNA. Both fields must remain; approved must not be rewritten as high RNA concordance or tissue specificity.
- PRAME retains nucleoplasm and additional plasma-membrane ICC/IF tags; CDH17 retains junctional and nucleoplasmic tags. CD276's tissue membranous/cytoplasmic summary and vesicular ICC/IF are distinct assay contexts. None identifies intact accessible antigen on EMC cells.

The XML identifies tissueExpression as HPA/IHC/tissue and cellExpression as HPA/ICC/IF. HPA subcellular documentation concerns immunofluorescently stained cells. The source contains cell-line localization information; it is not EMC tissue, normal-organ surface density or a binding assay. Differences between summaries should be retained as assay-context differences rather than harmonized into a single surface-positive boolean.

RNA records preserve consensusTissue and tissue blocks separately, even where both carry source HPA. The official tissue documentation says consensus nTPM uses the maximum across HPA/GTEx and across grouped subtissues. The extracted XML also includes pTPM and TPM level attributes; these are retained rather than relabelled nTPM. No unmatched normal/tumor ratio, safety threshold or donor-level inference is justified.

Version/license statements are accurate: every XML entry says version25 and Ensembl109/GRCh38.p13/GENCODE43; current documentation states25.1. The JSON has no explicit release field. The HPA license page applies CC BY4.0 to copyrightable database parts and explicitly retains third-party constraints. It does not grant a new blanket license over every external dataset. Exact response hashes identify the snapshots.

Command: bundled `python.exe -B -X utf8 .cache/atlas-normal-context-independent/verify.py`, exit0. `verification.json` records all gene counts, reliability descriptions, retained locations, RNA-unit counts and source hashes. This was a source check only; no tumor analysis rerun, manuscript/ultra review, source survey, tracked edits, mail or spending. Nothing running.
