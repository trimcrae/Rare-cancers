---
id: DOC-NEOANTIGEN-3-FINDING
title: "NEOANTIGEN-3 — the correspondence test re-run against a real validated reference set, and what the 15 real junction epitopes look like next to this repository's predictions"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# NEOANTIGEN-3 — the zero survives a real reference set, and the one checkable divergence is the **allele panel**, not the peptides

Follow-through lane. Builds on **PUB-NEOANTIGEN** (the correspondence machinery, run against a
reference set that turned out to contain no fusion-junction epitopes at all) and
**EPITOPE-BENCHMARK** (which supplied, for the first time, **n = 15** experimentally validated
cancer fusion-**junction** class I epitopes *with sequences*, across nine oncoproteins, plus
sequenced non-junction negative controls).

Writes confined to this directory. Nothing committed, added, pushed; no preflight; no manuscript
edited; no subagents; no network.

⛔ **Prediction is not presentation.** ⛔ **A validated epitope for BCR::ABL1 says nothing about
EWSR1::NR4A3.** Nine fusion oncoproteins are not a sample of fusions, and the census is a census of
published positives. Nothing below is an argument that any EMC peptide is or is not presentable, and
no clinical claim is made anywhere in this lane.

## 1 · The question

> Re-run against a reference set that actually contains fusion-junction epitopes, does this
> repository's predicted EWSR1::NR4A3 junction panel correspond to any validated junction epitope —
> and, more usefully, **do the 15 real ones and this repository's predicted ones look alike** in
> length, allele, breakpoint position and per-partner residue contribution?

## 2 · Merit

PUB-NEOANTIGEN's zero was uninterpretable in the direction that mattered: the 988 cached "fusion"
records were a keyword artifact containing **zero** cancer fusion-junction epitopes, so a miss
against them was a miss against nothing. EPITOPE-BENCHMARK's 15 are the first reference set in this
repository against which the miss can mean anything at all. The second question is the one with
paper-level value: a *distributional* comparison between what has actually been validated and what
this repository predicted is a checkable statement about **the prediction and its configuration**,
and configuration defects are fixable, unlike the wet-lab gate (B2) that stays closed.

## 3 · What a zero would and would not mean — stated before the result

Recorded **in advance** of §5, so the reading is not fitted to the outcome.

**A zero WOULD mean**, and only mean:

* No peptide in this repository's panel is one of the 15 already-validated junction epitopes, nor a
  fragment or extension of one, nor an I/L-isobaric look-alike of one. That is a statement about
  **overlap with a 15-element list**, nothing more.
* It would remove one specific confound: nobody can attribute a hypothetical future measurement on
  an EMC peptide to prior knowledge of a published epitope, and nobody can quote a published epitope
  as though it were evidence about this panel.
* Against the **negative controls**, a zero would additionally show the panel does not accidentally
  reproduce a non-junction peptide from an unrelated fusion.

**A zero would NOT mean:**

* **Not** that EWSR1::NR4A3 junction peptides are unpresentable, weakly presented, or unusual. The
  reference set contains **no EWSR1::NR4A3 record at all**, and could not, so it has no power to
  say anything about this fusion. Absence of overlap with nine other oncoproteins is not evidence
  about a tenth.
* **Not** a validation, a refutation, or a calibration of the MHCflurry predictions. Zero overlap is
  the **expected** result — nine unrelated fusions share no junction sequence with a tenth by
  construction — so this test's informative capacity is almost entirely in its *controls* and in
  any **non**-zero it happens to turn up.
* **Not** evidence about IEDB, whose contents were never reached here or by either parent lane.
* **Not** a power statement. n = 15 cannot support an inference test of any distributional
  difference; §5.2 reports proportions and explicitly declines to test them.

**A near-miss would have been the interesting outcome** — an isobaric or substring hit would flag a
sequence a mass spectrum could not disambiguate, which is exactly what the isobaric arm exists to
catch. One substring hit did occur, and §5.1 reports what it is and is not.

## 4 · The step taken

One offline generator, `neoantigen3_correspondence.py`, over two read-only inputs — the committed
`research/modalities/fusion-breakpoint-neoantigens.json` (174 distinct junction peptides across the
5 in-frame junctions; 11 ranked binders; MHCflurry 2.1.4 over a 10-allele panel) and the lane-local
`EPITOPE-BENCHMARK/epitope-records.json` (40 records). The **n = 15** reference set is rebuilt by
**reproducing EPITOPE-BENCHMARK's inclusion rule in code** and asserting the count is 15, so this
lane's reference set is that lane's, not a re-curation.

## 5 · Results

### 5.1 Correspondence — zero, with one live positive that is not a junction epitope

| query | reference | exact | substring | isobaric exact (I=L) | isobaric substring |
|---|---|---|---|---|---|
| 174 junction peptides | **15 validated junction epitopes** | **0** | **0** | **0** | **0** |
| 174 junction peptides | 5 sequenced non-junction negative controls | 0 | 0 | 0 | 0 |
| 174 junction peptides | 12 other sequenced records (prediction-only, binding-only, class II) | 0 | **1** | 0 | 0 |
| 11 predicted binders | **15 validated junction epitopes** | **0** | **0** | **0** | **0** |
| 11 predicted binders | 5 negative controls | 0 | 0 | 0 | 0 |
| 11 predicted binders | 12 other sequenced records | 0 | 0 | 0 | 0 |

A **context-level arm** repeats the test against the full 21-residue junction context of each of the
five junctions, so a validated epitope lying wholly inside a donor or acceptor flank — which the
seam-crossing 8–11mer windows could not catch — would still be found. It returns the same single hit.

**The matcher is demonstrably not dead.** Its exact arm recovers 15/15 running the reference set
against itself; its isobaric arm recovers 13 hits on 13 I/L-swapped copies of the reference
sequences; and the substring arm returns a real hit on the real query set.

**The one hit.** The repository's junction peptide `SQQSSSYGQQN` (junction `EWSR1_e7__NR4A3_e3`)
contains `SQQSSSYGQQ`, the **EWSR1 exon-7 donor motif** recorded in E38 — a clinical-genomics
breakpoint catalogue of EWSR1::FLI1 / ::ERG / ::FEV / ::WT1. What this is:

* An **independent corroboration of this repository's EWSR1 exon-7 donor-side seam sequence**,
  letter for letter, from a source outside this repository. That is a genuine, if small, external
  check on the transcript model's donor half at one of the five junctions.
* **Not** an epitope correspondence. E38 is **PREDICTION-ONLY** — the catalogue names *potential*
  immunogenic peptides and carries no immunological measurement — so it is excluded from the 15 by
  the benchmark's own rule.
* **Not** fusion-specific evidence. `SQQSSSYGQQ` is wild-type EWSR1; it is shared by *every* EWSR1
  exon-7 fusion, so it distinguishes nothing. The one repository peptide that contains it is
  `SQQSSSYGQQN`, whose only non-EWSR1 residue is the hybrid seam N.

**⛔ The EWSR1::FLI1 discrepancy stays unresolved and is not resolved by this hit.**
EPITOPE-BENCHMARK recorded that EWSR1::FLI1 returned **no** experimentally validated junction
epitope through nine queries, while the lane manuscript's §B1 names four peptides. E38 is the record
that mentions EWSR1::FLI1 breakpoint motifs, and it is prediction-only — so it supports **neither**
side. This lane assumes neither and carries the discrepancy forward untouched. It does, however,
make one consequence concrete: because the repository's e7 junction and any EWSR1 exon-7 Ewing-family
fusion share the identical 10-residue donor context, a future validated EWSR1 exon-7 junction
epitope would constrain only the **donor half** of this repository's e7 peptides — the seam residue
and everything C-terminal to it differ by construction.

### 5.2 Characterisation — where the two sets do and do not sit alike

Full tables in `CHARACTERISATION.md`. Proportions only; **no inference test is run** on n = 15.

| | validated (n = 15) | repo ranked binders (n = 11) |
|---|---|---|
| length | 9-mer ×11, 10-mer ×2, 11-mer ×2 | 9-mer ×3, 10-mer ×3, 11-mer ×5 |
| 8-mers | 0 | 0 (36 distinct 8-mer windows were screened; none ranked) |
| allotypes | A\*02:01 ×5, B\*07:02 ×3, C\*04:01 ×2, A\*24:02 ×2, B\*40:01, C\*12:03, A\*68:02 ×1 | A\*01:01 ×4, B\*07:02 ×3, B\*15:01 ×2, B\*35:01 ×1, B\*44:02 ×1 |
| loci | A ×8, B ×4, **C ×3** | A ×4, B ×7, **C ×0** |
| C-terminal anchor from the **acceptor** partner | 4 of 4 where the split is known | 11 of 11 |

**(a) The one concrete, checkable divergence is the allele panel — and it is a property of the
prediction's configuration, not of EMC.** Four of the seven allotypes that carry a validated
junction epitope are **not in the predictor's 10-allele panel** (A\*68:02, B\*40:01, C\*04:01,
C\*12:03), accounting for **5 of the 15** epitope-allele pairs. The panel contains **no HLA-C at
all**, while **2 of the 15** validated epitopes are C-restricted (3 of the 15 epitope-allele
pairs): `IFDRYGEEV`, one of the six MS-eluted entries, and `DKESEEEVS`, whose only reported
restrictions are C\*04:01 and C\*12:03.
An HLA-C-restricted junction epitope is therefore a *known-to-occur* outcome that this screen was
structurally unable to return. This is checkable, is about the screen, and is fixable by re-running
the screen over a wider panel.

**(b) A\*02:01 — where the validated set is deepest — returned zero ranked binders here.** Of the
three validated allotypes that *are* in the panel, only B\*07:02 produced any ranked binder. The
honest reading cuts both ways and both halves must travel together: the validated set's A\*02:01
depth is substantially **ascertainment** (the field's assays are A\*02:01-centric), so its 5/15 is
not a base rate; and equally, a screen returning nothing on the field's most-studied allotype is
worth knowing about, since 8 of the 11 ranked binders sit on allotypes (A\*01:01, B\*15:01,
B\*35:01, B\*44:02) that carry **no** validated junction epitope anywhere in the census. Neither
observation is evidence about presentation.

**(c) Length.** The validated set is 73 % 9-mers; the ranked binders are 27 % 9-mers and 45 %
11-mers. Both distributions have obvious non-biological drivers — the validated set is
A\*02:01-weighted and the field's assays favour 9-mers, while MHCflurry percentiles are normalised
within allele across lengths — so this is recorded as an observation, not as a defect and not as a
test. The single point where a source record speaks to length directly runs the *other* way and is
worth carrying: for `QFIDSSWYL` (E14) the 8-mer and the 10-mer registers did **not** stimulate, so
reactivity tracked one exact register.

**(d) Breakpoint position: mostly unknown, and reported as unknown.** The junction's position inside
the peptide is stated by the source record, or fixed by another record in the same fusion protein,
for only **4 of 15** — `SSKALQRPV` 3|6, `RYGEEVKEF` 5|4 (both stated), `EIFDRYGEEV` 9|1 and
`IFDRYGEEV` 8|1 (both derived from the E21 anchor `RYGEE|VKEF`, flagged as derived in the artifact).
The other **11 are UNKNOWN**: a peptide sequence alone does not say where its junction falls, and
this lane is offline. They are **not** counted as zero and **no** distribution is claimed over 15.

Within those 4, the acceptor contribution ranges 1–6 of 9–10 residues, and in all four the
C-terminal anchor comes from the **acceptor** partner. This repository's 11 ranked binders also draw
the C-terminal anchor from the acceptor in 11 of 11 — so on the one axis where a comparison is
possible, **the sets agree**. Where they differ is in degree: **8 of the 11 ranked binders take 8 or
more of their residues from NR4A3 and at most two from EWSR1**, a lopsidedness only one of the four
known validated splits approaches (`EIFDRYGEEV`, 9|1, donor-heavy in the opposite direction).

**(e) A consequence that is already measured, not speculated.** The extreme of that lopsidedness is
already recorded in this repository as a defect: the top-ranked `DMPCVQAQY` contributes **zero**
EWSR1 residues, and `junction-proteome-novelty.json` finds it — with three relatives — verbatim
inside **NR4A3 isoform Q92570-3**, verdict `BROKEN — a parent-filtered peptide matched a parent
protein`. The partner-split column and that committed proteome result are two views of the same
thing: a "junction" peptide whose sequence is almost entirely one partner's wild-type sequence is at
risk of not being junction-specific at all. That is a statement about the peptide-enumeration and
novelty filter, and it is checkable today.

## 6 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `neoantigen3-correspondence.json` (correspondence + characterisation, machine
  readable), `CHARACTERISATION.md` (rendered from it, do not hand-edit), generators
  `neoantigen3_correspondence.py` and `render_characterisation.py`, `checks/` (5 attempts, real exit
  codes, including one genuine failure).
* **Validation / baseline.** (i) The reference set is rebuilt by reproducing EPITOPE-BENCHMARK's
  inclusion rule in code, with `assert len(VALIDATED) == 15`, so a change to that lane's records
  would break this lane rather than silently drift. (ii) The matcher carries a **self-test in the
  artifact**: exact arm 15/15 against itself, isobaric arm 13/13 on I/L-swapped copies. (iii) The
  substring arm returns a **live positive** on the real query set, so no arm is reported zero
  without a demonstration it can be non-zero. (iv) Sequenced **non-junction negative controls** are
  tested separately, and the excluded (prediction-only / binding-only / class II) records are kept
  as a third stratum rather than merged in. (v) `assert` that every ranked binder is a member of the
  junction-peptide set, and that every peptide is locatable in its own junction context.
* **Provenance.** `fusion-breakpoint-neoantigens.json` `_utc` 2026-08-19T16:26:49Z (transcript
  model, ENST00000397938 / ENST00000395097, MHCflurry 2.1.4 / models 2.2.0);
  `EPITOPE-BENCHMARK/epitope-records.json`, PubMed/PMC MCP census of 2026-09-09, every record
  carrying a PMID. Both read from the existing checkout, read-only, nothing copied. Cost **$0** — no
  network, no GPU, no paid API.
* **Limitations.** ⛔ No presentation, efficacy, safety or clinical claim; no statement about
  EWSR1::NR4A3 presentability in either direction. (i) The reference set is 15 published
  **positives** across nine oncoproteins — selected for success, ascertainment-biased toward
  A\*02:01 and 9-mers, and a lower bound on the literature (EPITOPE-BENCHMARK's own §6 records that
  12 of 26 queries returned zero on term-mapping grounds). (ii) n = 15 supports no inference test;
  §5.2 reports proportions only. (iii) Breakpoint position is unknown for 11 of 15, and two of the
  four known are *derived*, not stated. (iv) I/L is the only isobaric ambiguity modelled; Q/K and
  residue-pair equivalences such as GG/N are not, so the isobaric arm is a floor on false-match
  risk, not a bound. (v) The repository's 11 binders are a threshold cut at presentation percentile;
  the full per-allele prediction matrix is not in the committed artifact, so "A\*02:01 returned zero"
  means no A\*02:01 peptide passed the weak cut, not that none was scored. (vi) The EWSR1::FLI1
  discrepancy is carried unresolved (§5.1). (vii) The transcript-model junction sequences are this
  repository's own; only the e7 donor half received any external corroboration here.
* **Stop condition.** Reached. The correspondence question is answered against a reference set that
  can bear it, the characterisation is done to the limit of what the records state, and the one
  actionable divergence (the allele panel) is a re-run decision for the paper owner, not another
  offline computation.

## 7 · Proposed, UNAPPLIED — no shared file was edited

Nothing outside this directory was touched; `systems/graph/*.json` and every manuscript are
unmodified. Offered for the paper owner's judgement, each to travel with §6's limitations:

1. For the neoantigen manuscript, replacing nothing and following PUB-NEOANTIGEN's proposed
   sentence — *"Re-run against the fifteen experimentally validated cancer fusion-junction class I
   epitopes reported across nine oncoproteins, none of this panel's 174 junction peptides or 11
   predicted binders corresponds to a validated epitope exactly, as a substring, or under
   leucine/isoleucine ambiguity; that absence of overlap is the expected result for an unrelated
   fusion and is not evidence about presentation."*
2. Also for the neoantigen manuscript, as a limitation on the screen itself — *"The presentation
   screen was run over a ten-allele panel containing no HLA-C allotype, while two of the fifteen
   validated fusion-junction epitopes, one of them identified by mass-spectrometric elution, are
   HLA-C-restricted; the screen could not have returned an HLA-C-restricted junction peptide."*

Whether either belongs in the manuscript is the paper owner's call.

## 8 · Next credible independent work (not done here, not authorised here)

1. **Re-run the MHCflurry screen over a wider allele panel that includes HLA-C** (and A\*68:02,
   B\*40:01), then re-report the ranked set. Bounded, offline-capable if the predictor is installed,
   and it directly closes the one divergence this lane found. It changes a **screen**, not a
   presentation claim.
2. **Repair the novelty filter** flagged `BROKEN` in `junction-proteome-novelty.json`, using the
   per-partner residue split as the discriminator: a candidate contributing zero residues from one
   partner is not junction-specific and should not be ranked as a fusion neoantigen.
3. **Resolve the EWSR1::FLI1 discrepancy** by reading §B1's own citations directly — still open,
   still not resolvable offline, and not to be settled by assuming either side.
4. **Recover the breakpoint positions** for the 11 validated epitopes whose split is unknown, from
   the source publications on the CI runner. This would make the position comparison in §5.2(d)
   answerable rather than mostly unknown; it cannot change §5.1.
