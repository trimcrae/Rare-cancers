---
id: DOC-PORTFOLIO-INVESTIGATION-PUB-NEOANTIGEN-2026-09-08
title: "PUB-NEOANTIGEN portfolio investigation — is any MEASURED peptide record an EWSR1::NR4A3 junction peptide, at exact correspondence and with a false-match control?"
level: L4
kind: investigation
status: live
date: 2026-09-08
last_verified: 2026-09-09
---

# PUB-NEOANTIGEN — measured external peptide evidence, exact correspondence, controls

Lane: `research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md`.
Writes confined to this directory. Nothing was committed, pushed, or added to the graph.

⛔ **Prediction is not presentation.** Every binding number in the lane manuscript is a
MHCflurry-2.0 prediction. Nothing below converts a prediction into a measurement, and nothing
below is a clinical claim.

## 1 · The question

Does any **measured** peptide record available to this repository correspond to an
EWSR1::NR4A3 fusion-junction peptide — at **exact sequence correspondence** — and would such a
correspondence be **attributable to the fusion** rather than to a false match (isobaric ambiguity,
a wild-type source, or a source antigen that is not a gene fusion at all)?

## 2 · Paper-level merit

The manuscript's §5 step 2 makes measured presentation the gate the whole modality case passes
through, and `emc-vaccine-development-path.md` grades that gate B2 — "the highest-value single
experiment in the ledger". The manuscript states there is no EMC immunopeptidomic dataset. It does
**not** state what the *general* measured record contains for fusion junctions, and §B1 of the
companion asserts, from three citations, that the validated fusion-junction epitope literature is
"individual sequences across a few fusions". That is a claim about the size of a measured set. This
repository holds a cached pull of measured epitope records (`iedb-validated-epitope-cache.json`,
2026-09-01), and **its composition has never been audited**. Patient relevance is direct: a public
(off-the-shelf TCR-T / soluble-TCR) product rests on a junction peptide being a real, measured
ligand; if no measured record of any fusion-junction ligand exists, the personalised-by-necessity
conclusion the paper already reaches is the only supportable one, and the paper should say why on
measured grounds rather than on citation count.

## 3 · The evidence gap, and how it differs from completed or held work

* **Not B2 re-opened.** B2 asks for new mass spectrometry on EMC tissue — wet lab, out of scope and
  closed. This asks only what *already-measured, already-cached* records contain.
* **Not the proteome novelty test.** `junction-proteome-novelty.json` tested the 174 junction
  peptides against the *reviewed human proteome* (170 novel, 4 hits in an NR4A3 isoform Q92570-3).
  That is a self-sequence test against protein databases. It is not a test against **measured
  peptide observations**, and it applies no MS-specific false-match control.
* **Not the S24 threshold calibration.** `S24-CALIBRATION.md` fetched IEDB to calibrate a
  presentation-percentile cut. Its committed artifact `vaccine-threshold-calibration.json` has
  **empty arms** (`_ingest.n_raw_fusion_rows: 0`) and records the verdict **WITHHELD** because
  `_fusion_fetch_is_complete` is `false`. A separate, later cache
  (`iedb-validated-epitope-cache.json`, 6108 raw fusion rows → 988 normalised records) **did**
  arrive, and **nobody has read what is in it**. S24's own alternatives table also sets an
  immunopeptidome atlas aside as answering a different question, so the correspondence question was
  never asked of any measured set.
* **Not the HLA population-coverage work** (parked adverse, another lane): no coverage figure is
  computed, quoted, or revised here.
* **Not the method-watch trigger.** `TRG-JUNCTION-PHLA` is a forward-looking, title-only,
  120-day EuropePMC watch for a *capability*. It does not test correspondence of this repository's
  peptides against measured records.

## 4 · The bounded step taken

A single offline test, `junction_measured_correspondence.py`, over two already-committed inputs.
No network (the one network attempt is recorded as a failure in `checks/`), no GPU, no paid API.

Inputs: the 174 distinct `novel_peptides` of the five in-frame junctions and the 11 predicted
binders (`fusion-breakpoint-neoantigens.json`, transcript model); the 988 arm-F + 965 arm-N
normalised measured records (`iedb-validated-epitope-cache.json`; positive assay outcome only,
lengths 8–11, 4-digit HLA-A/B/C restriction) — 1224 distinct measured peptides.

**Results** (`junction-measured-correspondence.json`):

| test | result |
|---|---|
| T1 exact correspondence, junction peptide == measured peptide | **0 of 174** |
| T2 substring correspondence in either direction | **0** |
| T3 isobaric false-match control (I/L collapsed, the ambiguity ordinary MS/MS cannot resolve) | **0** |
| T4 arm-F provenance control: records whose source antigen is a human **gene-fusion** oncoprotein | **0 of 988**, over **44** distinct source-antigen strings |
| T5 can these records distinguish measured **presentation** (eluted-ligand MS) from measured binding? | **No** |
| source antigen naming EWSR1, NR4A3 or TAF15 anywhere in either arm | **none** |

**T4 is the substantive finding.** The 988 "fusion" records are a **keyword artifact of a
source-antigen name pattern**: 931 are viral or housekeeping proteins merely *named* "fusion"
(poxvirus entry-fusion complex OPG095/OPG086/OPG094, paramyxovirus fusion glycoprotein F0,
ubiquitin–ribosomal-protein fusion proteins, vacuolar fusion proteins CCZ1/MON1, sperm–egg fusion
proteins Izumo/Juno/TMEM95), and the rest are germline read-through or chimeric transcripts
(PALM2-AKAP2, CNK3/IPCEF1, ERCC6-PGBD3, FAU) or genes whose *name* contains "fusion partner"
(TCF3 fusion partner). The single record the regex flagged as gene-fusion-related,
"PML-RARA-regulated adapter molecule 1", is a normal human protein *regulated by* PML-RARA, not a
fusion junction. **Not one cancer gene-fusion junction epitope is present.** The full 44-name
census with per-antigen record counts is in the artifact, so the classification is auditable.

**T5 is the honest limit on any hit this test could have produced.** The cache retains only which
IEDB table a record came from. `mhc_search` mixes eluted-ligand mass spectrometry with in-vitro
binding assays, so even an exact hit could not have been called *presentation* from these records.

## 5 · What this does and does not license

* It **does** establish that this repository's measured-epitope holdings contain **no** peptide
  corresponding to any EWSR1::NR4A3 junction peptide, exactly or isobarically, and **no** measured
  epitope from any cancer fusion junction at all.
* It **does** show that the number 988 must never be quoted as a count of validated fusion-junction
  epitopes; read at the source-antigen level it is zero, which is *consistent with* §B1's "a handful
  in the literature" but is **not** an independent confirmation of it.
* It **does not** claim absence in IEDB. The fetch behind the cache is recorded as **incomplete**
  (`_fusion_fetch_is_complete: false`); a complete pull could contain BCR::ABL1, SS18::SSX or
  *EWSR1*::*FLI1* records that this cache does not. The finding is a reading of what arrived, plus
  the demonstration that **what arrived is a keyword artifact rather than a short fusion set** —
  i.e. the incompleteness is not the only defect, and a re-fetch alone would not fix the inclusion
  rule.
* It **does not** bear on whether a junction peptide is presented on an EMC cell. That is B2, it is
  wet-lab, and it stays open and unmoved.

## 6 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `junction-measured-correspondence.json` (+ `junction_measured_correspondence.py`).
* **Validation / baseline.** T1 is checked against three progressively weaker correspondence
  criteria (exact → substring → isobaric); all three return zero, so the zero is not a strictness
  artifact. The script asserts that every ranked binder is a member of the novel-peptide set before
  testing. T4's classification is published as a full antigen census, not as a summary count, so a
  reader can re-bucket it. The known positive control for the *reverse* direction already exists
  outside this test: `junction-proteome-novelty.json` shows `DMPCVQAQY` — a predicted binder — does
  occur verbatim in NR4A3 isoform Q92570-3, so a measured observation of that sequence could not be
  attributed to the fusion. The correspondence machinery is therefore not "always zero": the
  peptide set contains at least one sequence a measured hit could not disambiguate.
* **Provenance.** `fusion-breakpoint-neoantigens.json` (`_utc` 2026-08-19T16:26:49Z, transcript
  model, ENST00000397938 / ENST00000395097); `iedb-validated-epitope-cache.json` (`_utc`
  2026-09-01T21:25:43Z, IEDB IQ-API `mhc_search` + `tcell_search`). Both read from the existing
  checkout; nothing copied, nothing fetched. Cost $0.
* **Limitations.** (i) The measured set is one incomplete cached pull, not IEDB. (ii) Assay method
  is unrecoverable, so presentation and binding are not separable (T5). (iii) The cache is filtered
  to 8–11mers with 4-digit HLA-A/B/C restriction, so class II and unrestricted records were never
  in scope. (iv) I/L is the only isobaric ambiguity modelled; Q/K and residue-pair equivalences such
  as GG/N are not, so T3 is a floor on false-match risk, not a bound on it. (v) MHCflurry is trained
  on IEDB, so the two inputs are not independent — but that bias would create hits, and there are
  none, which is the direction that makes a zero safe to report.
* **Stop condition.** Reached. The question is answered for the records this repository holds, and
  the next move is not another local computation.

## 7 · The next credible independent step (NOT taken here)

An IEDB re-fetch that (a) selects on **assay method** so eluted-ligand mass spectrometry is
separable from binding, and (b) replaces the source-antigen **name** pattern with an explicit list
of cancer fusion oncoproteins, then asks the same correspondence question. That is a networked
fetch; the direct attempt from this sandbox failed at the egress proxy
(`checks/01-uniprot-fetch`, CONNECT 403), so it belongs in the CI runner and is out of scope for
this lane, which may not commit or dispatch. Recorded as a dependency, not as work in progress.

**Proposed, UNAPPLIED, for the lane manuscript** — no shared file was edited. §5 step 2 could carry
one measured sentence in place of a citation count: *"A search of the epitope records held here
(1224 distinct measured 8–11mers, positive outcome, HLA-A/B/C-restricted) returns no peptide
corresponding to any junction in this panel, exactly or under the leucine/isoleucine ambiguity that
mass spectrometry cannot resolve; the 988 records that entered on a 'fusion' source-antigen name
are viral and housekeeping proteins named 'fusion', not cancer fusion junctions."* Whether the
manuscript should carry it at all is the paper owner's call, since the underlying fetch is
incomplete and the sentence must travel with that caveat.
