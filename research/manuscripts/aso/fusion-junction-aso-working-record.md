---
id: DOC-FUSION-JUNCTION-ASO-WORKING-RECORD
title: "Working record — fusion-junction ASO analyses, provenance and correction history"
level: L3
kind: register
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `manuscript` from its location under research/manuscripts/.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
> # THIS IS THE WORKING RECORD, NOT THE SUBMISSION
>
> **The submitted manuscript is
> [`fusion-junction-aso-research-article.md`](./fusion-junction-aso-research-article.md).** This
> file is its provenance archive: every analysis in full, every superseded value, and the complete
> correction history that repository rule 1.2 requires be registered rather than dropped.
>
> It exists because those two audiences are incompatible. A journal reader needs one thesis, one
> denominator and no version history; a maintainer needs to know which numbers were withdrawn, when,
> and why. Keeping both in one file produced a 24,000-word document in which — as an editorial review
> put it on 2026-08-12 — *no sentence stated a result the manuscript did not itself withdraw, censor
> or disown*. Splitting them is what makes each readable.
>
> **This file is not a parallel draft of the paper and must never become one.** It holds analyses and
> provenance; the submission holds the argument. Where they overlap on a number, the artifact under
> `research/modalities/` is the one home and both point at it.

# A fusion-selective antisense oligonucleotide against the EWSR1::NR4A3 breakpoint junction: RNA-level fusion-exclusivity that the NR4A3 degrader cannot reach

> **Correction record.** This manuscript was subject to a retraction and correction on 2026-08-06:
> a defective exon index produced a chimeric seam no plausible breakpoint generates, and every
> design attributed to a "real" EWSR1 exon-*n* :: NR4A3 exon-3 junction before that date is
> withdrawn. The panels were rebuilt, the withdrawal partially lifted, and the corrected result
> **refutes half of the retracted headline** rather than restoring it. The full record — what went
> wrong, what the corrected reading is, what remains withdrawn and why — is
> **[Appendix A](#appendix-a--retraction-and-correction-record-2026-08-06)**. It is kept in full
> because the superseded values stay quotable and a reader who meets one elsewhere must be able to
> find what replaced it.

> **In-silico design / feasibility draft (2026-06).** No wet lab; no molecule synthesized; **no new
> GPU run was performed** — the real results cited here are CPU outputs: the committed gapmer designs
> [`../modalities/junction-aso-designs.json`](../../modalities/junction-aso-designs.json) (5 fusion-specific
> gapmers), a transcriptome-wide off-target screen
> [`../modalities/junction-aso-offtarget.json`](../../modalities/junction-aso-offtarget.json) (0 of 5 free of
> gap-spanning near-matches), and a junction-siRNA design set
> [`../modalities/junction-sirna-designs.json`](../../modalities/junction-sirna-designs.json) (0 of 5 pass;
> min GC 73.7%), a full-transcriptome (uncapped, 186,185-transcript) off-target + accessibility + siRNA-seed
> evaluation [`../modalities/aso-insilico-evaluation.json`](../../modalities/aso-insilico-evaluation.json) (0 of 5
> canonical gapmers off-target-free; true ≤1-mismatch counts 8–95, not the capped "50"), a per-breakpoint
> feasibility scan
> [`../modalities/junction-breakpoint-scan.json`](../../modalities/junction-breakpoint-scan.json) (390 modelled
> breakpoints; 243, or 62%, favorable; the canonical one is not), and a gap-mismatch-resolved off-target
> screen on a favorable breakpoint
> [`../modalities/junction-aso-offtarget-bp200-8-gapres.json`](../../modalities/junction-aso-offtarget-bp200-8-gapres.json),
> re-scored under a graded fold-discrimination model
> [`../modalities/junction-aso-offtarget-bp200-8-gapres-graded.json`](../../modalities/junction-aso-offtarget-bp200-8-gapres-graded.json)
> (**0 of 5 gapmers predicted off-target-clean**; the designs separate by predicted cleavage load over more
> than an order of magnitude, and it is that separation — not a clean call — that the screen supports.
> ⚠ *Superseded, retained: "2 of 5 gapmers predicted clean — zero true RNase-H cleavage risk", which counted
> every gap-disrupted near-match as zero-cleavable; see §3a-quater and Appendix A, entry 68*), corroborated
> by an uncapped full-transcriptome screen on the same favorable breakpoint
> [`../modalities/aso-insilico-evaluation-bp200-8.json`](../../modalities/aso-insilico-evaluation-bp200-8.json)
> (4 of 5 gapmers with zero ≤1-mismatch off-targets; 5 of 5 with zero exact — vs 0 of 5 at that threshold at
> the canonical junction; a *stricter-threshold* count, not a cleanliness call).
> ⛔ **The clause that stood here is RETRACTED** (see the retraction block above) and is retained
> verbatim so it stays quotable as *withdrawn*, not as current: *"and — closing the prior 'only
> modelled breakpoints' gap — the **full pipeline run on the real recurrent EWSR1 exon-12/exon-7 ::
> NR4A3 exon-3 junctions** built exon-exact from Ensembl (`aso-insilico-evaluation-e12n3.json`,
> `junction-aso-offtarget-e7n3.json`, etc.; real junctions are 37–62% GC not 75–81%, and E7::N3
> yields a gapmer predicted clean on both screens)."* Those junctions were **not** exon-exact: they
> resume NR4A3 at residue 361 against a corrected plausible range of [1, 1]. The "only modelled
> breakpoints" gap the clause claimed to close is therefore **OPEN**, and the corrected GC figures
> are UNKNOWN pending the CI regeneration.
> ✅ **Both halves of that last sentence are now closed, and they close differently (2026-08-06,
> §3a-sexies).** ⚠ *Superseded, retained: "the corrected GC figures are UNKNOWN pending the CI
> regeneration."* The regeneration ran. The "only modelled breakpoints" gap is closed **for two
> junctions, E7::N3 and E12::N3** — not the five the withdrawn clause implied. The GC half of the
> clause survives on new numbers (real seams 37.5–56.2%, not 75–81%); the specificity half does
> **not** — no corrected design at either junction is free of gap-spanning near-matches, so *"E7::N3
> yields a gapmer predicted clean on both screens"* is contradicted by the corrected screen and
> stays withdrawn.
> The modelled-breakpoint results that remain show feasibility is
> **breakpoint-conditional but breakpoint-selectable**: specificity and chemistry at the *canonical* modelled
> junction are poor, but that is a property of that junction position — a clear majority of modelled
> breakpoints yield clean, in-band, fusion-specific designs — not of the modality. **The fusion-selectivity rationale in one line:** the breakpoint mRNA seam is
> present *only* in the chimera, so an RNase-H gapmer (or siRNA) targeting the junction silences
> EWSR1::NR4A3 while sparing wild-type *EWSR1* and wild-type *NR4A3* — true fusion-exclusivity, which an
> LBD-binding degrader (identical domain in fusion and wild-type) cannot achieve. Every clinical/quantitative
> claim is cited, computed from committed repo output, or flagged as a design hypothesis. Nothing here is a
> validated drug or clinical evidence. **An adversarial self-review of this manuscript — deficiencies and the
> fixes applied — is recorded in [`fusion-junction-aso-paper-redteam.md`](./fusion-junction-aso-paper-redteam.md).**

---

## Abstract

Extraskeletal myxoid chondrosarcoma (EMC) is defined in the large majority of cases by an in-frame fusion
of *EWSR1* (less often *TAF15*, and rarely TCF12/TFG/FUS) to the orphan nuclear receptor *NR4A3*, on an
otherwise "quiet" genome with few recurrent secondary mutations [Sjögren; Panagopoulos]. The companion
NR4A3-degrader program in this repo targets the **NR4A3 ligand-binding domain (LBD)** — a domain whose
sequence is *identical* in the fusion and in wild-type NR4A3 — so that agent is NR4A3-selective but **not
fusion-selective**, and it carries the residual liability of also removing tumour-suppressive wild-type
NR4A3 [Mullican; Safe & Karki]. This manuscript pursues the one feature the degrader cannot offer: **true
fusion-exclusivity at the RNA level.** The chimeric mRNA contains a breakpoint *junction sequence* that
exists in no normal transcript; an antisense gapmer whose central DNA window straddles that seam directs
RNase-H1 cleavage of the fusion transcript while sparing both parent mRNAs by sequence, and a
junction-spanning siRNA offers a parallel route. We report the one real, committed computational result —
**5 fusion-specific candidate gapmers** designed against the modelled EWSR1::NR4A3 junction
([`junction-aso-designs.json`](../../modalities/junction-aso-designs.json)), each drawing bases from both
sides of the seam and absent as a perfect complement from either parent CDS — together with the honest
caveat that surfaces immediately: this junction is **GC-rich (~75–81% GC)**, outside the usual comfort
zone, and would need chemistry tuning. Two further real, committed CPU results sharpen this caveat: a
transcriptome-wide off-target screen (blastn-short vs human RefSeq RNA) finds **0 of 5** gapmers free of
gap-spanning (RNase-H-cleavable) near-matches, and a GC-tolerant junction siRNA route does **not** rescue
the chemistry — its lowest-GC fusion-specific guide is still **73.7% GC**, so **0 of 5** siRNA guides pass
all filters. The honest synthesis is that this *modelled* breakpoint sequence is intrinsically GC-rich and
low-complexity, hurting gapmer chemistry, siRNA GC, and predicted specificity at once — a property of this
junction, not of the modality. A new per-breakpoint feasibility scan
([`junction-breakpoint-scan.json`](../../modalities/junction-breakpoint-scan.json)) confirms this directly:
sweeping **390 modelled breakpoints** (an arbitrary codon-space grid; the 62% is an upper bound on
*designable* positions, not a real-patient breakpoint frequency), the reference position is unfavorable but a
majority pass a GC/complexity/parent-substring triage and yield balanced (~50% GC) in-band gapmer *and* siRNA
designs. Triage-passing is necessary but **not** sufficient: the gapmer the scan picks as in-band-best at the
worked 200/8 example actually carries the most off-target cleavage risks there, so a per-oligo BLAST screen
must follow the triage (§3a-ter/§3a-quater). So feasibility is
**breakpoint-conditional but breakpoint-selectable**: junction sequence-favorability is a tractable
selection step (sequence the patient's breakpoint, triage it, then BLAST-screen a favorable design), not a
roadblock — with the honest bounds that these breakpoints are *modelled, not exon-exact*, that "favorable"
is a GC/complexity triage rather than the full BLAST screen, and that clinical design must still be re-run
on each patient's sequenced breakpoint. We then extend the analysis from one partner to the disease: a pan-partner atlas
([`nr4a3-fusion-junction-atlas.json`](../../modalities/nr4a3-fusion-junction-atlas.json)) grades **231
donor-exon × NR4A3-acceptor-exon pairs across EWSR1, TAF15, TCF12, FUS and TFG**, finds **38** frame-compatible
junctions of which **every one** yields at least one junction-spanning, parent-sparing design, and
⚠ *superseded, retained: "**207** … pairs across EWSR1, TAF15, TCF12 and FUS" and "**32** frame-compatible" —
the fifth partner, TFG, was added 2026-08-12 and contributes 24 graded pairs and 6 frame-compatible
junctions. This summary paragraph was never rewritten when it landed, so the record's own opening
understated the corpus that the rest of the record, the atlas and the manuscript all report.*
reports that **a single 16-mer gapmer is fusion-exclusive at three different partners' junctions at once**
(EWSR1 e12, TAF15 e11 and FUS e10, each joined to NR4A3 exon 3) because the three donors are identical
over the eight bases immediately 5′ of their breakpoints — so the deployable artifact is not necessarily
*n* bespoke oligos. The full transcriptome pipeline was then run at those junctions — **the first
off-target screens at any non-EWSR1 NR4A3 fusion** — and reproduces the identical panel from a live
Ensembl read by an independent code path; that shared design is the **cleanest of the ten distinct
sequences screened at the FET junctions** (8 predicted cleavage risks against 13–50; 0 exact and 1
≤1-mismatch off-target across 186,185 transcripts) — ⚠ *superseded, retained: "the cleanest of the twenty
screened."* Those twenty screens were **ten distinct oligos**, because the same five were screened at
each of three junctions and returned identical results, so the denominator triple-counted; and TCF12
designs score lower still (best 1, §3a-nonies). ⚠ *Superseded, retained: "The conclusion is unchanged
and is stated as such: **0 of 5 designs are clean at every junction screened**, so what the screens
support is a rank ordering for a wet-lab assay, not a clean call."* With all 38 junctions screened and
orientation filtered, **nine designs at six junctions across four partners carry no hybridisable
near-match**, over the 47 of 183 designs whose hit lists are complete enough to assess — see
Appendix B.4. The caution the superseded sentence carried is still right in its narrower form: that is
a floor over a subset, not a total, and it is not a statement about cleavage. We then specify what else is computable *now* without any GPU (extended
tiling and a breakpoint-keyed per-patient panel). On delivery we correct a framing rather than claim
progress: **it is three routes with different requirements, not one gate.** The missing EMC surface
antigen — which the tumour-tissue data refuses — is a prerequisite of the *systemic receptor-targeted*
route only; local/intratumoural and **inhaled/pulmonary** administration need no antigen, and EMC's
distant spread is lung-dominant (35–45% of patients, primarily lung; median time to metastasis ≈28
months). Inhaled and intratracheal oligonucleotide delivery producing specific gene silencing *in
tumours growing in the lung* is an active preclinical field, in other tumour types, in animals — and the
inhaled-oligonucleotide *route* has itself reached patients, including an inhaled antisense
oligonucleotide in a phase 1 trial and an inhaled siRNA in phase 2b-3, in non-oncology indications. We
state plainly that no such record concerns EMC, a sarcoma lung metastasis, a fusion target, or any
solid-tumour target: what is established is that the route is deliverable and tolerable in humans, not
that it reaches a metastatic nodule. We ask others to run one decisive experiment: junction-ASO versus
scrambled-control knockdown in patient-derived EMC lines (USZ-EMC [Bangerter]; NCC-EMC [Iwata]), with
specificity confirmed by sparing of the parental transcripts. ⛔ **We state the prior art rather than
imply novelty we do not have: junction-directed oligonucleotides against fusion oncogenes are a continuous
35-year lineage that has reached clinical testing, and the modality has already been generalised across ten
indications by other groups (§1a).** ⚠ *Superseded, retained: "The platform generalises to any
recurrent-fusion cancer with a defined breakpoint; EMC is the proof-of-concept entry indication."* — true,
and not ours to claim. **This paper's method-level novelty is nil; its one first-in-kind claim is
indication-level**: across 5,153 unique retrieved records, four name EWSR1::NR4A3 and none is an
oligonucleotide study, so EMC is an untouched indication for an established modality — and what we add
beyond that is an EMC-specific degrader-versus-ASO argument, a breakpoint-favorability *selection* step, and
the negative that this junction is intrinsically bad.

---

## 1. Background and the fusion-selectivity rationale

EMC's defining lesion creates a chimeric transcription factor: the N-terminal low-complexity /
transactivation region of EWSR1 (a FET-family protein) fused to most of NR4A3 (NOR-1), an orphan member of
the NR4A nuclear-receptor subfamily [Sjögren; Panagopoulos]. *EWSR1::NR4A3* is the dominant variant;
*TAF15::NR4A3* accounts for a substantial minority, with rarer partners (TCF12, TFG, FUS) [Panagopoulos].
Critically, EMC otherwise carries **few recurrent secondary mutations** — a "quiet genome" — so the fusion
is, to a first approximation, the single clonal driver of the disease [Panagopoulos; and see the
EMC-program roadmap]. A therapy that neutralises the fusion transcript should therefore engage essentially
every tumour cell at baseline. This lowers *baseline* heterogeneity but does **not** guarantee the absence of
*acquired* resistance: downstream-pathway reactivation, delivery-driven heterogeneity of exposure, and — a
risk specific to a junction-targeted oligo — a **point mutation at or near the patient's breakpoint that
abolishes oligo complementarity** are all plausible escape routes. Clonality is an advantage, not a guarantee
of no escape.

**The central differentiator — why this paper exists alongside the degrader.** The repo's lead modality is
a PROTAC/molecular-glue degrader that engages the **NR4A3 ligand-binding domain** and recruits an E3 ligase
to remove the protein (see [`nr4a3-degrader-paper.md`](../degrader/nr4a3-degrader-paper.md)). That LBD is retained
near-intact in the fusion, and its amino-acid sequence is **identical** to that of wild-type NR4A3. A
ligand that binds the fusion's LBD therefore cannot, in principle, distinguish the fusion from wild-type
NR4A3: the degrader is **NR4A3-selective but not fusion-selective**. The degrader paper handles this
honestly — its selectivity work is *paralogue* selectivity (NR4A3 vs NR4A1/NR4A2), not *fusion-vs-wildtype*
selectivity.
⚠ *Superseded, retained (2026-08-14): "and it is bounded by NR4A3's own tumour-suppressor roles (combined
NR4A1/NR4A3 loss causes AML [Mullican]; NR4A3 is tumour-suppressive in HCC/breast/lymphoma [Safe & Karki]).
Removing wild-type NR4A3 systemically is thus a real liability the degrader must manage." The AML phenotype
requires **combined** Nr4a1/Nr4a3 loss and single nulls do not produce it, so it does not support a liability
attaching to loss of NR4A3 alone. Withdrawn from the submission manuscript and not to be requoted —
[Appendix B.10](#appendix-b10--the-wild-type-nr4a3-liability-argument-withdrawn-from-the-introduction-2026-08-14-0).*

The fusion **mRNA junction** dissolves this problem at the sequence level. The breakpoint seam — the few
nucleotides where the retained EWSR1 exon is spliced to the retained NR4A3 exon — is a contiguous sequence
that appears in **neither** parent transcript. An antisense oligonucleotide complementary to that seam, or
an siRNA spanning it, can engage the chimera while each wild-type mRNA matches only one half of the oligo.
This is the RNA-level expression of "fusion-unique": fusion-exclusivity **by sequence**, achieving exactly
the discrimination the LBD degrader cannot. The two modalities are complementary, not redundant — the
degrader removes the oncoprotein (and, accepting the liability, wild-type NR4A3 too); the junction ASO
removes only the chimeric transcript.

---

## 1a. Related work — 35 years of junction-directed oligonucleotides, and what is left for this paper

⛔ **THE METHOD-LEVEL NOVELTY OF THIS PAPER IS NIL, AND WE STATE THAT BEFORE ANYTHING ELSE.** Targeting a
fusion breakpoint with an oligonucleotide is not new, is not recent, and is not rare. It is a continuous
35-year lineage that has reached clinical testing. Everything this manuscript proposes at the level of
*mechanism* — junction-spanning oligo, discrimination by base-pairing, cleavage by RNase H, a scrambled
control, a parental-sparing readout — has been published, in several cancers, by other groups. **What is new
here is the indication and nothing else.**

The accounting below is machine-retrieved, not recalled: two Europe PMC corpora totalling **5,385 rows /
5,153 unique records**, run on GitHub runners and anchored with the quoted text in
[`lit-targets-aso-verify.json`](lit-targets-aso-verify.json); the full narrative, every verbatim quote and
the per-fusion table are in [`aso-citations-priorart-2026-08-08.md`](aso-citations-priorart-2026-08-08.md).
Every identifier in this section traces to that fetch record.

**(i) The idea, the mechanism and the control, all published in the 1990s.** Junction-directed antisense
against **BCR-ABL** with a scrambled control and demonstrated sparing of normal marrow cells is
**PMID 1794439** (1991). The closest mechanistic precedent is **PMID 9049825** (1997) — antisense at a
*sarcoma* fusion **breakpoint** in which *"exogenously added RNase H was found to be required for translation
inhibition"*: junction targeting, base-pair discrimination and RNase-H cleavage, i.e. this manuscript's
entire mechanism, 29 years earlier. EWS-fusion antisense abolishing Ewing tumorigenicity is
**PMID 7566963** (1995) and **PMID 9005992** (1997). The catalytic-nucleic-acid route ran in parallel:
**PMID 7987829**, **PMID 8127665**, **PMID 9150886**, and **PMID 9224607** — the last a warning this
manuscript should carry rather than rediscover, that *"several hammerhead ribozymes with relatively long
junction-recognition sequences have poor substrate-specificity."* Long junction-spanning arms do not buy
selectivity.

**(ii) The fusion-exclusivity rationale was written down as a general principle in 2005.**
**PMID 16083345**: *"the junction point at the mRNA level offers a target for short therapeutic nucleic
acids that is present only in the cancer cells and not in the normal tissues of a patient. Several teams
have, therefore, investigated the activity of antisense oligonucleotides and siRNAs targeted against the
junction point."* §1's rationale is that sentence. Junction oligo *plus a delivery vehicle* — the shape of
§3c — is **PMID 14620508** (2003).

**(iii) Parental sparing has been demonstrated repeatedly, at the bench, in other fusions.** This is the
endpoint §4 proposes, and it is not an open question in the field: **PMID 33241214** (10 siRNAs tiled across
the FGFR3-TACC3 breakpoint; 7 of 10 depleted the fusion and *"did not affect levels of wild-type (WT) FGFR3
or TACC3"*), **PMID 36265509** (BRD4-NUTM1, *"without affecting the endogenous expression of the parent
genes"*), **PMID 36302174** (shRNAs *"tiled over the fusion junction"* for DNAJB1-PRKACA in two PDX models).
In sarcoma specifically: **PMID 20648560** (EWS-FLI1 breakpoint siRNA), **PMID 27261335** (PAX3-FOXO1,
RGD-targeted nanoparticles), **PMID 20198325** and **PMID 23716114** (SS18-SSX1, systemic nanoparticle
delivery). In prostate and leukaemia: **PMID 23052253**, **PMID 31614005** (TMPRSS2/ERG), **PMID 21846246**
(PML-RARα), **PMID 31104089** (BCR-ABL LNP), **PMID 40991849** (RUNX1::RUNX1T1 siRNA-LNP in primary AML
cells, 2025); review **PMID 42110475** (2026).

**(iv) The design methodology exists too.** **PMID 26627251** names the exact difficulty §3a-ter attacks —
*"in some cases (e.g., a fusion junction site) region choice is restricted. In these instances, alternative
approaches are necessary."* **PMID 31728968** is a protocols chapter supplying *"guidelines and procedures
for RNAi design of chimeric RNAs… and necessary controls"*: §4's control design is a solved, published
protocol.

**(v) ⛔ A junction-targeted agent has been developed to the point of proposing clinical testing.**
**PMID 27166877** — a bi-shRNA against *"the identical type 1 translocation junction region of the
EWS/FLI1 transcribed mRNA"*, reporting 85–92 % target knockdown and stating that the results
*"provide the justification to initiate clinical testing"*. A reviewer knows this lineage exists.
The manuscript must not read as though it does not.

⚠ **SUPERSEDED, RETAINED: "has been taken into clinical testing … follow-through in patients is
PMID 36780200" (corrected 2026-08-12).** That sentence was wrong twice over and had reached the
submission draft. **PMID 36780200 is Vigil** — an autologous tumour-cell therapy expressing a
**bi-shRNA against *furin*** plus GM-CSF — and its own abstract says so in the file this repository
already held (`origin/literature-cache:literature/aso-refmeta-journals/PMC10150239.txt`: *"Vigil is
a novel autologous tumor cell therapy expressing bi-shRNA furin/GMCSF plasmid"*). EWS/FLI1 enters
that paper only as a **ctDNA breakpoint marker for response monitoring**, not as the agent's target.
And PMID 27166877 is titled *Preclinical* Justification: it argues **for** initiating clinical
testing, so citing it as evidence that testing **happened** inverts what it says. No trial of a
junction-directed EWS/FLI1 agent is anchored anywhere in this repository. ⛔ **The tell was in the
title of each paper**, and neither `lint_citations` nor `lint_claims` can catch this class: both
identifiers are real, both are anchored to genuine fetch products, and the sentence attached to them
was hedged. Provenance and claim strength are orthogonal to whether the cited paper is *about* the
thing claimed — that check is human, and here it took an adversarial reader asking what the agent
in PMID 36780200 actually targets.

**(vi) And the delivery gate has been passed once, in a rare fusion-driven cancer.** **PMID 37980543** —
GalNAc-conjugated siRNA against the **DNAJB1::PRKACA fusion junction** in fibrolamellar HCC. This is the
closest program-level precedent to what §3–§4 describe, and it is evidence that the §3c delivery gate is
passable *in principle*. ⚠ It is not evidence that it is passable **for EMC**: GalNAc/ASGPR is a
liver-specific receptor handle, and EMC has no equivalent. §3c remains unsolved.

### What that leaves — an indication-level claim, and three smaller ones

| claim | status |
|---|---|
| Targeting a fusion junction with an oligonucleotide | **not novel** — 1991, continuously since |
| The fusion-exclusivity rationale | **not novel** — general principle, 2005 review (PMID 16083345) |
| RNase-H cleavage at a *sarcoma* fusion breakpoint | **not novel** — PMID 9049825, 1997 |
| Demonstrating parental sparing | **not novel** — done in ≥4 fusions |
| The §4 decisive experiment | **not novel** — a published protocol (PMID 31728968), executed in ≥6 fusion cancers |
| "The platform generalises to any recurrent-fusion cancer" | **not novel, and already generalised** — by other groups, in ten indications, one in the clinic |
| **EMC / EWSR1::NR4A3 specifically** | **⭐ untouched** — see the accounting below |

**The one first-in-kind claim, stated at exactly its weight: an indication-level first.** Across 5,153 unique
records, **four** name EWSR1::NR4A3 at title/abstract level; those four are three distinct papers
(**PMID 40762284**, **PMID 29937513**, **PMID 25097177**) and **not one is an oligonucleotide study**, so the
count of junction-directed oligonucleotide work against EWSR1::NR4A3 — or against *any* NR4A3 fusion —
is **zero**.

✅ **THOSE THREE IDENTIFIERS ARE NOW VERIFIED, AND THE FETCH ALSO SHOWS THE FRAMING WAS TOO KIND TO
ITSELF (2026-08-12).** ⚠ *Superseded, retained: they were flagged earlier the same day as unverified,
because they appeared in `lit-targets-aso-verify.json` only inside a hand-written narrative field —
no title, no authors, no abstract — while that fusion's machine-generated `example_pmids` list was
empty and every other fusion's was populated. An identifier written into a prose field and read back
as though it were a fetch is the exact failure the citation gate exists for, and it sits in the one
position the gate cannot see: the gate matches identifiers against any tracked JSON without asking
whether the match is a record or a sentence.* A `resultType=core` fetch resolved all three, and they
are real papers — but **only one of the three is an EMC paper**:

| PMID | what it actually is |
|---|---|
| 29937513 | an EMC case report — an actionable *KIT* mutation (Int J Mol Sci, 2018) |
| 40762284 | **bladder** cancer — NR4A3 and anoikis resistance via EWSR1 (Cancer Biol Ther, 2025) |
| 25097177 | primary **myelofibrosis** CD34+ miRNA–mRNA analysis (Blood, 2014) |

So the honest statement of the search result is: **4 of 5,153 records mention EWSR1::NR4A3 at
title/abstract level, those four are three papers, only one concerns EMC, and none is an
oligonucleotide study.** The absence claim survives — it rests on the corpus-wide count of zero
oligonucleotide studies against any NR4A3 fusion, not on these three — but a reader who pulls the
three should not find them oversold. ⭐ **That second clause is now load-bearing rather than incidental**: since §3a-septies the
paper addresses *any* NR4A3 fusion — TAF15, TCF12 and FUS as well as EWSR1 — so the untouched indication
is the whole NR4A3-rearranged disease and not one partner of it. Against **108** junction-plus-oligo records for BCR::ABL1 and **37** for EWSR1::FLI1, EMC is not a
thin search result; it is an untouched indication. ⚠ The method is title/abstract-only, so every count is a
**lower bound** — which is the correct direction here, because a lower-bound method cannot manufacture a zero
it did not observe, though it can miss a paper that names the fusion only in its body.

Three smaller contributions survive, and none of them is a methodological first:

1. **The degrader-vs-ASO argument is EMC-specific and is this paper's real contribution.** No prior
   junction-oligo paper had to argue against a competing modality that is *sequence-identical to wild-type*.
   That argument exists only because NR4A3's LBD is retained intact in the fusion and NR4A3 is itself a
   tumour suppressor (**PMID 17515897**, **PMID 33106376**). It is not available in Ewing or FLC and it is
   not a junction-oligo insight.
2. **Breakpoint-favorability as a *selection* step** (§3a-ter/§3a-quater) — sweeping candidate breakpoints on
   GC, complexity and off-target load and reporting that favorability is breakpoint-conditional. The nearest
   prior work (**PMID 26627251**) optimises an siRNA *within* a fixed junction; it does not triage *across*
   junctions. Modest, and a methods contribution rather than a claim about EMC.
3. **The honest negative that the reference junction is intrinsically bad** — 75–81 % GC, low-complexity,
   poor predicted specificity. Nobody has reported it, and it is publishable on its own.

**One gap in the prior art is real and is a chemistry gap, not an opening.** No **gapmer** — as opposed to
siRNA, shRNA, ribozyme or unmodified ODN — appears directed at a fusion junction in a modern LNA/cEt
architecture. That is not a niche the field overlooked: per §3a-quater, single-base discrimination by an
unmodified RNase-H-active gapmer is roughly five-fold (**PMID 23963702**) and at 16-mer length may be absent
altogether (**PMID 7567450**), which is a reason the field has largely used RNAi at junctions. The gap is
evidence the chemistry is hard here, not evidence it is unexplored terrain.

⛔ **Framing, therefore, throughout this manuscript:** we **apply an established modality to EMC for the
first time and report where EMC's junction sequence makes it hard.** We do not propose junction-directed
oligonucleotides, and no sentence here should be read as claiming a new capability, a new mechanism, or
efficacy, safety or clinical readiness for any design.

## 2. The approach: junction-spanning gapmer or siRNA

Two transcript-level mechanisms can exploit the junction; both require the active sequence to **straddle**
the breakpoint so that fusion-exclusivity is enforced by base-pairing.

**(a) RNase-H1 gapmer (lead).** A gapmer is a short oligo with a central DNA "gap" flanked by modified
"wings" (LNA — locked nucleic acid — or cEt — constrained ethyl). The wings raise affinity and nuclease
resistance; the DNA gap, once hybridised to the target, recruits endogenous RNase-H1 to cleave the RNA
strand [Crooke et al. 2021]. For fusion-exclusivity the central DNA gap must span the junction, because
RNase-H1 cleaves within the DNA:RNA duplex of the gap — so the cleaved bond sits across the tumour-specific
seam.

> **Where the discrimination really lives — a precise (and limiting) statement.** "A parent transcript
> matches only one wing" is *necessary but not sufficient*. RNase-H1 needs a contiguous DNA:RNA duplex of
> roughly ≥5–6 base pairs across the **gap** to cleave; the wings (LNA/cEt) do not support cleavage. So
> fusion-discrimination is set by how many junction-**unique** bases fall *inside the 6-nt catalytic gap on
> each side of the seam*, not by the whole 16-mer. The committed `specificity_margin` is computed oligo-wide
> (`min(bases_from_EWSR1, bases_from_NR4A3)` across all 16 nt), so it **overstates** true gap-level
> discriminating power, and the design only requires the junction to fall *somewhere* in the gap
> (`gap_start < j < gap_end`) — which permits a 1/5 split where one parent shares 5 of the 6 gap bases. The
> defensible design rule (a fix this red-team adopts going forward, see §3b) is to require the junction near
> the **gap centre** with ≥2–3 junction-unique bases on each side *within the gap*, and to treat the
> transcriptome off-target screen (§3a-bis/§3a-quater), not the oligo-wide margin, as the operative
> specificity filter. A parent transcript that happens to match the full gap plus a flank *can* be cleaved —
> which is exactly why the gap-mismatch-resolved off-target screen (§3a-quater) is the load-bearing analysis.

The committed designs (§3) use a 16-mer **5-6-5** LNA/DNA/LNA architecture; the design script's docstring
also references the common **5-10-5** gapmer layout as the standard 20-mer template [`junction_aso.py`].

**(b) Junction-spanning siRNA (parallel route).** An siRNA / shRNA whose guide strand is centred on the
junction loads into RISC and directs Ago2 cleavage of the chimeric mRNA. siRNA chemistry (2′-OMe / 2′-F,
phosphorothioate, and conjugation handles) is mature, and RISC tolerates the GC-rich seam differently from
RNase-H, so the siRNA route is a genuine fallback if gapmer chemistry proves intractable at this GC content
(§6). The selectivity logic is the same: the guide must cover the seam, and a single-nucleotide-resolved
seed mismatch against either parent transcript is what buys fusion-exclusivity. siRNA off-target
(seed-mediated) behaviour differs from ASO off-target behaviour, so the two routes need separate
specificity screens.

**Chemistry options (both routes).** Backbone phosphorothioate for stability/protein binding; sugar
modifications (LNA/cEt for gapmers; 2′-OMe/2′-F for siRNA); and — central to the unsolved delivery problem
(§3c) — conjugation handles (GalNAc is hepatocyte-directed and therefore *not* useful for a soft-tissue
sarcoma; a tumour-receptor-directed conjugate is what EMC would need).

---

## 3. Computational groundwork

### 3a. What already exists (real, committed output)

[`research/modalities/junction_aso.py`](../../modalities/junction_aso.py) fetches the RefSeq CDS of *EWSR1*
(NM_005243) and *NR4A3* (NM_006981) from NCBI, builds the **modelled** fusion CDS at the canonical
protein-level breakpoint (EWSR1 kept to codon 264; NR4A3 retained from codon 2 — flagged in the output as
an assumption), and tiles 16-mer 5-6-5 gapmers whose central DNA gap spans the junction. It keeps only
oligos that (i) draw bases from **both** sides of the seam and (ii) are **not** a perfect complement of
either parent CDS. The committed result
([`junction-aso-designs.json`](../../modalities/junction-aso-designs.json)) reports **5 fusion-specific
candidate gapmers** (`n_candidates = 5`, `n_fusion_specific = 5`), e.g. the top design antisense
`5′-ACGCAGGGCTGCTGCC-3′` (target mRNA `GGCAGCAGCCCTGCGT`, 8 bases from each side of the seam,
specificity margin 8). The modelled junction context is `…TACGGGCAGCAG|CCCTGCGTCCAA…`.

**The honest design caveat surfaces immediately and is reported as a real finding:** this junction is
**GC-rich**, with the top candidates at **75–81% GC** (75.0% and 81.2% across the five), well outside the
usual 40–60% gapmer comfort zone. None carry a G-quadruplex (≥4 consecutive G) motif (`has_G4_motif:
false` for all five), but the high GC alone implies elevated melting temperature, self-structure and
potential aggregation/tox risk that would require chemistry tuning (wing chemistry, length, or the siRNA
route). This is exactly the kind of constraint a design tool should expose up front; it is recorded here as
a real, committed result, not hidden.

> **Integrity flag (the breakpoint is modelled, and "canonical" is a label of convenience — not a validated
> clinical breakpoint).** The committed designs use a *modelled reference* breakpoint (EWSR1 kept to codon
> 264, NR4A3 from codon 2; the JSON marks `_breakpoint_model.assumption = true`). We call this position
> "canonical" only because it is the script default shared with the companion neoantigen work — **it is not a
> validated common patient junction.** Two honest consequences. (1) The codon-264 cut coincides with the
> EWSR1 1–264 IDR/transactivation boundary used elsewhere in this repo, i.e. it is a *protein-domain*
> landmark, not an observed mRNA breakpoint. (2) The **real** recurrent EMC junctions are exon-level and join
> **predominantly to NR4A3 exon 3** (the companion breakpoint-resolved work resolved EWSR1 exons 7/9/10/11/12/13
> → NR4A3 exon 3; [`novel-modalities.md`](../modality-census/novel-modalities.md) §3.3), whereas "NR4A3 from codon 2" retains
> almost the entire NR4A3 CDS — so the *modelled* junction seam is not the seam of the commonly reported
> EWSR1 exon-7/12 :: NR4A3 exon-3 fusion. ✅ *The rank-order marker that stood here is RESOLVED from the
> primary literature:* **PMID 12378528** reports EWS exon 12 :: CHN exon 3 as type 1 (10 of 18 EMCs) and
> exon 13 :: exon 3 as type 5, with 12 of 14 genomic breaks in CHN intron 2; corroborated by
> **PMID 11679947** and **PMID 9060841** (`CHN` = `TEC` = *NR4A3*).
> ⛔ *Superseded, retained: "The full pipeline **has since been run on those real exon-3 junctions**
> (§3a-quinquies), which turn out to be far more GC-favorable than this modelled reference."* It was
> run on a seam graded `SEAM_NOT_PRODUCED`, and the corrected comparison is **UNKNOWN** until the CI
> regeneration lands. ⚠ Note what this does to the paragraph's own argument: the sentence above still
> stands — the modelled codon-2 seam is **not** the seam of the exon-3 fusion — but this manuscript
> no longer has *any* computed exon-3 seam to contrast it with. The gap is named, not filled.
> The practical upshot
> is unchanged — every clinical design must be re-derived from the patient's **sequenced** fusion transcript
> (§3b) — but the reader should not read "canonical" as "the breakpoint patients actually carry." The five
> sequences are design hypotheses on a modelled seam, not a drug.

### 3a-bis. Off-target screen and siRNA route — now done for the modelled breakpoint (real, committed)

Three further CPU jobs were run on the modelled-breakpoint designs and committed as real outputs — a BLAST
gap-spanning off-target screen (i), a GC-tolerant siRNA route (ii), and an uncapped full-transcriptome
evaluation that also scores accessibility and siRNA-seed load (iii). Together they turn the abstract's GC
caveat into a quantified, honest verdict on *this* junction.

**(i) Transcriptome-wide off-target screen
([`junction-aso-offtarget.json`](../../modalities/junction-aso-offtarget.json)).**
[`junction_aso_offtarget.py`](../../modalities/junction_aso_offtarget.py) BLASTs each gapmer (blastn-short,
filter off) against human RefSeq RNA (`txid9606`) via the NCBI BLAST API and counts near-matches
(≥14/16 identical), flagging those that cover the central DNA gap (positions 6–11) — the
RNase-H-cleavable liability. **Of 5 gapmers, 4 returned** (one BLAST query transiently failed); **every
returned gapmer hit the HITLIST cap of 50 near-matches, and all 50 were classified gap-spanning**, so
`n_oligos_no_gap_spanning_offtarget = 0` of 5. The top candidate (`ACGCAGGGCTGCTGCC`) had 50 gap-spanning
near-matches spread across unrelated genes (e.g. *OTOG*, *SPTBN2*, *MAP3K13*, *SLC2A9*).

> **Over-call caveat (reported as honestly as the result).** The HITLIST was capped at 50 and the
> low-complexity filter was **off**, so on a GC-rich, low-complexity window like this junction the screen
> **over-calls** near-matches: the 50 figure is a floor / over-estimate in character, not an exact
> off-target count. The *qualitative* signal is nonetheless robust — these particular gapmers are
> **specificity-poor**: a GC-rich, low-complexity seam matches many transcripts at ≥14/16 identity, and
> gap-spanning matches are the most concerning class. This is predicted specificity, not validated; only the
> §4 wet-lab parental-/off-target-sparing controls can confirm it.

**(ii) GC-tolerant junction siRNA route
([`junction-sirna-designs.json`](../../modalities/junction-sirna-designs.json)).**
[`junction_sirna.py`](../../modalities/junction_sirna.py) designs junction-spanning 19-mer siRNA guides
(RISC/Ago2, GC window 30–52%) as the GC-tolerant fallback of §2b. It returns **5 fusion-specific guides,
but 0 pass all filters**, because the **minimum GC among the fusion-specific guides is 73.7%** — far above
the 30–52% target window. So the siRNA route **does not rescue** the GC problem at this breakpoint; the same
GC-rich seam that troubles the gapmer also disqualifies every siRNA guide.

**(iii) Full-transcriptome (uncapped) off-target + accessibility + siRNA-seed evaluation
([`aso-insilico-evaluation.json`](../../modalities/aso-insilico-evaluation.json)).**
[`aso_insilico.py`](../../modalities/aso_insilico.py) re-screens the same five canonical-breakpoint gapmers
against the **entire human RefSeq RNA transcriptome (GRCh38.p14; 186,185 transcripts)** downloaded in full —
an **uncapped, local** scan that removes the §3a-bis(i) HITLIST-50 over-call and yields true counts. It adds
two axes the BLAST screen does not: ViennaRNA target-site **accessibility** (potency) and an **siRNA
seed-region** off-target module. The picture it draws of the canonical junction is more nuanced than the
capped screen, and still negative on the bottom line:
- **True off-target counts are real, not a floor — and lower than the capped "50" suggested.** All five
  gapmers have **0 exact** transcriptome matches; their **≤1-mismatch** full-length counts are
  **8, 16, 17, 58, 95** (the two 81.2 %-GC designs are by far the worst, at 58 and 95). So the best canonical
  gapmer (`ACGCAGGGCTGCTGCC`) has only 8 near-complementary off-target sites genome-wide — but
  **`n_candidates_zero_offtarget = 0`**: none is clean, consistent with the canonical junction being
  unfavorable. (These are full-16-mer ≤1-mismatch hits, *not* gap-resolved, so like the BLAST screen they
  still over-count true RNase-H cleavage risk — the gap-resolution of §3a-quater is what separates cleavable
  from non-cleavable.)
  Two method bounds on "true counts": the seed-and-extend scan finds every ≤1-**substitution** off-target
  (the pigeonhole guarantee) but **not** 1-nt insertion/deletion (bulged) off-targets, and it counts
  **sense-strand transcript** matches only — the cleavage-relevant orientation — not genomic/antisense
  complementarity. "Uncapped true counts" should be read with those two scoping choices in mind.
- **Target site is moderately accessible** (mean unpaired probability **0.34–0.42** across the five) — i.e.
  potency is not obviously gated by mRNA structure at this junction; specificity, not accessibility, is the
  reference junction's problem. *Caveat:* this is a **local 180-nt fold** equilibrium proxy — it ignores
  long-range pairing that could sequester the site in the full transcript (so it can *over-estimate*
  accessibility) and is only a rough correlate of ASO potency (no kinetics, no in-cell protein occupancy);
  the 0.34–0.42 spread is within method noise and is **not** a meaningful potency ranking among the five.
- **The siRNA seed route carries its own, large liability, reported honestly:** only **2 of 5** designs
  present a guide seed that actually **straddles the junction** (the fusion-unique-seed goal), and the
  seed-match off-target load is enormous (**~21,000–119,000** transcriptome seed sites), because a GC-rich
  seed is intrinsically promiscuous. This is an independent reason the GC-rich canonical seam is hard for
  RISC, complementing the GC-window failure in (ii).

**Synthesis — feasibility is breakpoint-conditional, not modality-limited.** At the canonical *modelled*
breakpoint, the EWSR1::NR4A3 junction sequence is simultaneously **GC-rich and low-complexity**, and this
single property hurts three things at once: (i) gapmer chemistry (75–81% GC), (ii) siRNA GC (min 73.7%),
and (iii) predicted specificity (many gap-spanning off-targets). This is a property of **this junction
sequence**, not of the ASO/siRNA modality. Crucially, real patients carry **≥7 distinct in-frame
breakpoints** (the companion neoantigen work: EWSR1 exons 7/9/10/11/12/13 → predominantly NR4A3 exon 3;
[`novel-modalities.md`](../modality-census/novel-modalities.md) §3.3 — ⛔ **that enumeration is retracted**; see §3b.4 and
[`fusion-neoantigen-retraction.json`](../../modalities/fusion-neoantigen-retraction.json). Breakpoint
heterogeneity in EMC is a literature fact and is not in doubt; the specific seven-junction resolution is),
some of which are likely more favorable. The
conclusion is therefore that ASO/siRNA feasibility is **breakpoint-conditional**: designs must be re-run on
the patient's *sequenced* breakpoint, and junction sequence-favorability (GC content, complexity,
off-target load) becomes a **patient/breakpoint selection criterion**. This tempers but does not overturn
the route's standing — the *mechanism* (knockdown of an addicted fusion transcript) remains the most
mechanistically unambiguous of the fusion-exclusive routes (conditional on breakpoint, gated by delivery),
and the per-breakpoint scan below (§3a-ter) shows that a clear
majority of modelled breakpoints *do* yield in-band designs (triage-clean, not yet off-target-screened) — so the reference junction's poor
chemistry/specificity is a property of **that position**, not of the modality.

### 3a-ter. Per-breakpoint feasibility scan — favorability is a tractable selection step (real, committed)

The breakpoint-conditional hypothesis above makes a falsifiable prediction: if the canonical junction's
GC/specificity problem is a property of *that* position rather than of the modality, then sweeping the
breakpoint position should reveal many *other* positions whose junction is favorable. We tested this
directly. [`junction_breakpoint_scan.py`](../../modalities/junction_breakpoint_scan.py) sweeps a grid of
**390 modelled in-frame breakpoints** (EWSR1 kept-length 200–300 codons × NR4A3 start 2–30 codons) and
triages each junction by junction-window GC (±10 nt), ±12 nt Shannon entropy, low-complexity repeat, and
whether a *fusion-specific* gapmer or siRNA exists with GC in the 40–60% comfort band. The committed result
([`junction-breakpoint-scan.json`](../../modalities/junction-breakpoint-scan.json)) **largely resolves the
breakpoint-conditional concern in the route's favor**:

- **243 of 390 modelled breakpoints (62%) are FAVORABLE** — i.e. a fusion-specific gapmer or siRNA exists
  with GC inside the 40–60% band. A clear majority of positions yield a chemically clean, specific design.
- The **canonical breakpoint (EWSR1 keep 264 / NR4A3 from 2) is NOT favorable**, exactly as the §3a / §3a-bis
  findings predicted: junction GC ±10 nt = **80%**, minimum gapmer GC **75.0%**, minimum siRNA GC **73.7%**,
  and **no in-band design** (`best_oligo: null`). The canonical position is genuinely a hard one.
- A **well-balanced in-band example** (EWSR1 keep 200 / NR4A3 from 8) has junction GC ±10 nt = **50.0%** and
  yields a fusion-specific 5-6-5 gapmer at **GC 50.0%** *together with* an in-band siRNA guide (**GC 52.6%**)
  — i.e. balanced GC/complexity on both routes. **Crucial caveat, and the paper's own thesis in miniature:**
  the gapmer the scan picks as 200/8's in-band best is `5′-GCTATACGGCTGTGTA-3′`, and the §3a-quater
  gap-resolved BLAST screen shows that exact oligo carries **29 full-gap-duplex near-matches** — the *worst* of
  the five gapmers at this breakpoint. GC/complexity triage passing does **not** predict a low off-target load;
  the lowest-load designs at 200/8 are the slightly higher-GC `GGGCTATACGGCTGTG` (62.5%) and
  `AGGGCTATACGGCTGT` (56.2%) — **lowest, not clean** (§3a-quater). So 200/8 illustrates *both* halves of the thesis: breakpoint-level
  favorability (in-band on both routes) **and** the separate, decisive need for per-oligo off-target
  selection on top of it. (200/8 was chosen by hand as an in-band example on both modalities, not by the
  scan's `most_favorable` rank; that rank — EWSR1 204 / NR4A3 16, 35% junction GC — is an artifact of ranking
  by GC-extremity and in fact has **no** in-band gapmer at all (`best_gapmer_in_band_gc: null`), only a 42.1%
  siRNA, so it is less useful than 200/8 despite being the script's top-ranked "favorable.")

**Honest caveats on the scan (stated as plainly as the result):**

1. **These are MODELLED breakpoint positions** — a codon-space sensitivity sweep, not exon-exact clinical
   breakpoints. The 62% is a property of the swept grid, **not** a claim about how often real patients carry
   a favorable breakpoint; the companion exon work (EWSR1 exons 7/9/10/11/12/13 → predominantly NR4A3 exon 3;
   [`novel-modalities.md`](../modality-census/novel-modalities.md) §3.3 — enumeration retracted, §3b.4) is bracketed in codon
   space here, not mapped exon-exact. ⭐ **That refusal to map is why this scan survives the retraction
   intact**, and it is the one place in the lane where declining to be precise turned out to be the correct
   engineering call rather than conservatism.
2. **"Favorable" = passes a GC/complexity/parent-substring TRIAGE**, not the full transcriptome BLAST
   off-target screen of §3a-bis(i). A breakpoint chosen as favorable still owes that BLAST screen before any
   specificity claim.
3. **Real clinical design still needs the patient's actually-sequenced breakpoint** — the scan narrows the
   design space and shows favorable positions exist; it does not substitute for sequencing the patient's
   chimera.

**What the scan changes.** It converts the breakpoint-conditional caveat from a near-fatal-sounding risk
into a **tractable selection step**. The canonical junction is unfavorable, but it is one position out of
many; a clear majority of modelled breakpoints give balanced (~50% GC), fusion-specific designs on both the
gapmer and siRNA routes. The GC/specificity problem documented in §3a/§3a-bis is therefore a property of the
**canonical position**, not of the ASO/siRNA modality. The practical consequence is a concrete workflow:
sequence the patient's breakpoint, triage it with this scan, and — for a favorable hit — run the §3a-bis(i)
BLAST off-target screen on that specific design (triage alone is not enough — §3a-quater). This supports the
route's standing as the most mechanistically *unambiguous* of the fusion-exclusive options (gated by
delivery), with breakpoint-favorability now demonstrated to be selectable rather than a roadblock.

### 3a-quater. Two off-target screens on a favorable breakpoint — gap-resolved BLAST + uncapped full-transcriptome
We ran the full §3a-bis(i) off-target screen *directly on the favorable 200/8 breakpoint* (junction GC
50 %), then **resolved each near-match to the gap-mismatch level** — because RNase-H cleavage requires the
central DNA gap (the 6 nt the gapmer cleaves through) to be base-paired: a near-match whose mismatch falls
*inside* the gap is **predicted strongly disfavoured** for cleavage and is treated here as not a real
liability ([`junction-aso-offtarget-bp200-8-gapres.json`](../../modalities/junction-aso-offtarget-bp200-8-gapres.json)).
This is informative, and positive — with one explicit assumption flagged below:
- **GC-triage alone is necessary but not sufficient**, and the coarse "gap-spanning" count *over-states*
  risk. Every near-match at this breakpoint is a weak **14/16** (2-mismatch) hit to a real gene
  (CSMD2, ADAMTSL2, DDR1, SLC66A1…), versus the reference junction's stronger 15/16 hits.
- **⛔ NO GAPMER IN THIS PANEL IS PREDICTED OFF-TARGET-CLEAN. The earlier "2 of 5" was an artefact of
  assuming a gap-internal mismatch ABOLISHES cleavage, and the primary literature does not support that.**
  Two retrieved sources set the bounds, and neither permits a clean/dirty call:
  **PMID 23963702** measures ~**5-fold** discrimination for a single-nucleotide change with an *unmodified*
  RNase-H-active ASO, and reaches **>100-fold only with positional chemical modifications** these designs do
  not carry; **PMID 7567450** reports that 12–13mers centred on the mismatch discriminate well but
  **16mers "did not discriminate efficiently"** — and **every design here is a 16-mer**, so the source that
  matches this geometry is the one that argues against discrimination altogether. The panel is therefore
  re-scored as a **residual predicted cleavage load** under both bounds
  ([`junction-aso-offtarget-bp200-8-gapres-graded.json`](../../modalities/junction-aso-offtarget-bp200-8-gapres-graded.json),
  derived offline from the same committed screen so the hit set is held fixed and only the scoring moves):

  | gapmer (antisense) | GC | off-target near-matches | full-gap-duplex | gap-disrupted | residual load, 5-fold model | residual load, no-discrimination model |
  |---|---|---|---|---|---|---|
  | `AGGGCTATACGGCTGT` | 56.2 % | 1 | 0 | 1 | **0.2** | **1.0** |
  | `GGGCTATACGGCTGTG` | 62.5 % | 21 | 0 | 21 | 3.24–4.2 | 21.0 |
  | `GGCTATACGGCTGTGT` | — | 36 | 15 | 21 | 16.8–19.2 | 36.0 |
  | `AAGGGCTATACGGCTG` | — | 28 | 27 | 1 | 27.2 | 28.0 |
  | `GCTATACGGCTGTGTA` | — | 38 | 29 | 9 | 30.16–30.8 | 38.0 |

  **Zero designs reach a residual load of 0 under either bound.** The interval width is *truncation* of the
  stored off-target list, not statistical uncertainty; the two rows with a complete list are exact.
- **What survives is a rank order, and it is the top two that are model-invariant.** `AGGGCTATACGGCTGT` is the
  best design under both bounds by more than an order of magnitude, `GGGCTATACGGCTGTG` second; the ordering of
  the remaining three **swaps between the two models**, so only the top two may be quoted as a ranking. This is
  a weaker and more defensible statement than "clean": the screen ranks candidates for a wet-lab specificity
  assay, it does not clear any of them.
- So **per-oligo selection is as important as breakpoint selection**, and the deciding filter is the
  gap-mismatch-resolved off-target screen, not raw GC or raw near-match count.
- **An orthogonal, uncapped full-transcriptome screen ranks the same two designs first — and its extra
  cleanliness is a threshold artefact, not extra reassurance.** We re-ran the §3a-bis(iii)
  uncapped evaluation (full RefSeq, 186,185 transcripts; seed-and-extend) *on this same 200/8 favorable
  breakpoint* ([`aso-insilico-evaluation-bp200-8.json`](../../modalities/aso-insilico-evaluation-bp200-8.json)).
  The contrast with the canonical junction is stark: **all 5 gapmers have 0 exact off-targets and 4 of 5 have
  0 near-perfect (≤1-mismatch) off-targets** transcriptome-wide (the fifth has just 1), where the *canonical*
  designs had 0 of 5 at that threshold and 8–95 ≤1-mismatch hits.
  The siRNA-seed load also collapses at this breakpoint (the junction-straddling seed of `GCTATACGGCTGTGTA`
  matches **3,366** transcriptome sites, vs ~119,000 for the GC-rich reference seed). The two screens
  **agree on the top two** (`AGGGCTATACGGCTGT`, `GGGCTATACGGCTGTG`): both also
  have zero ≤1-mismatch off-targets in the uncapped scan. But for the other three they *disagree sharply* —
  the uncapped scan reports `GCTATACGGCTGTGTA` and `GGCTATACGGCTGTGT` as 0 and 1 ≤1-mismatch off-target,
  while the gap-resolved BLAST finds **29 and 15** full-gap-duplex near-matches. The reason is
  structural: the uncapped scan's ≤1-mismatch (≥15/16) cutoff **cannot see** the 14/16 (2-mismatch) hits that
  drive the BLAST counts, so its "4 of 5 with zero ≤1-mismatch hits" is cleaner only because it uses a
  *stricter match threshold*, not because those oligos are safer. ⛔ **Neither screen supports calling any
  design clean.** The uncapped scan's zero counts are zeros *at ≥15/16*; the graded re-score above shows that
  the 14/16 hits the wider test admits carry non-zero predicted cleavage under both literature bounds.

**Reading.** At a favorable breakpoint, the full workflow — breakpoint triage → per-oligo BLAST →
gap-mismatch resolution, corroborated by an independent uncapped full-transcriptome screen — **separates the
designs by predicted off-target cleavage load across more than an order of magnitude**, a separation the
GC-rich reference junction could not offer. ⛔ **It does not yield a predicted off-target-clean gapmer: under
both literature-supported discrimination models the count is 0 of 5** (Appendix A, entry 68 records the
superseded "2 of 5"). So breakpoint choice demonstrably *moves* predicted specificity — *predicted*, not
demonstrated — while the absolute claim the earlier draft made is withdrawn. Honest bounds remain
and are load-bearing: the ranking rests on a fold-discrimination prior taken from two papers, only one of
which is at this oligo length (PMID 7567450, and it is the pessimistic one); the
breakpoint is *modelled* not patient-sequenced; and **delivery (§3c) is the separate, still-unsolved
gate.** We therefore call this route the most mechanistically *unambiguous* fusion-exclusive option —
knockdown of an addicted, fusion-only transcript, with no protein-conformation guesswork — **conditional on
breakpoint-favorability and gated by delivery.** That is a narrower and more defensible claim than "most
de-risked": the degrader's dominant risk (sparing wild-type NR4A3) differs in kind from the ASO's (delivery),
and neither is strictly more de-risked overall.

### 3a-quinquies. ⛔ RETRACTED — the "REAL clinical junctions" section (EWSR1 e12 / e7 :: NR4A3 e3) — superseded by §3a-sexies

> ⛔⛔ **EVERYTHING IN THIS SECTION IS RETRACTED (2026-08-06). DO NOT QUOTE ANY DESIGN, SEQUENCE, GC
> VALUE, OFF-TARGET COUNT OR CONCLUSION FROM IT.** The junctions it calls "real" and "exon-exact"
> resume NR4A3 at **residue 361**, which
> [`fusion-neoantigen-retraction.json`](../../modalities/fusion-neoantigen-retraction.json) grades
> `SEAM_NOT_PRODUCED` against a corrected plausible resume range of **[1, 1]**. The full reasoning,
> the E11::N3 root cause and the three cited files that have never existed are in the retraction
> block at the top of this document. The text is **retained rather than deleted** so that a reader
> who has already quoted it can find it marked withdrawn — this repo's standing rule (CLAUDE.md §1:
> corrections go in an appendix, superseded numbers are registered, never silently dropped).
>
> ⚠ **Do not repair this section by editing its numbers.** Not one of them survives: every oligo in
> the panel spans the seam by construction, so every design changes when the NR4A3 half changes. It
> is replaced wholesale by the corrected panel when `emc-expression-datasets.yml`
> `mode: aso-junction` has run, and not before.
>
> ✅ **REPLACED WHOLESALE BY §3a-sexies, 2026-08-06.** This section stays
> retracted and is not edited. ⚠ *One correction to the sentence above, which was a live pointer and
> not just a caveat:* `mode: aso-junction` regenerates the **audit and the design panels** and
> deliberately does not publish, but it does **not** run the BLAST or the uncapped scan, so it could
> never have replaced this section on its own. The screens were run through
> [`aso-offtarget.yml`](../../../.github/workflows/aso-offtarget.yml) `real_junctions: "12:3 7:3"`,
> which is the only route in this repository that runs them.

The red-team's lead open gap was that every screen above ran on *modelled* breakpoints, never on the
**actually recurrent** EWSR1::NR4A3 exon junctions. That gap is now closed. We built the real fusion CDS
directly from Ensembl MANE/canonical exon structure (reusing the companion `fusion_breakpoints.gene_model`;
self-checked `translate(CDS) == Ensembl protein`, NR4A3 C-terminus intact) and ran the **full** pipeline —
design → gap-resolved BLAST → uncapped full-transcriptome eval — on the two most commonly reported junctions,
**EWSR1 exon-12 :: NR4A3 exon-3** (the most common) and **EWSR1 exon-7 :: NR4A3 exon-3**
([`junction-aso-designs-e12n3.json`](../../modalities/junction-aso-designs-e12n3.json),
[`junction-aso-offtarget-e12n3.json`](../../modalities/junction-aso-offtarget-e12n3.json),
[`aso-insilico-evaluation-e12n3.json`](../../modalities/aso-insilico-evaluation-e12n3.json), and the `-e7n3`
counterparts). Both share the NR4A3 exon-3 right-side seam (`…|TTGTCCGTACAG`), as expected.

> ⛔ **THIS IS THE SENTENCE THAT HID THE DEFECT, AND IT IS KEPT HERE FOR THAT REASON.** `TTGTCCGTACAG`
> is NR4A3 CDS nt 1081–1092, i.e. the chimera resuming at residue 361. The two panels shared it
> because **one defect produced both**, not because two independent constructions converged — and
> "as expected" turned that shared error into apparent corroboration. The EWSR1 side, which *was*
> correct, is what made the agreement look like a check. **Agreement between two artifacts is
> evidence only when they can fail independently.**

Two findings, one of them important and positive:

- **The GC-rich "chemistry problem" was largely an artifact of the non-real reference junction.** At the
  *real* junctions the fusion-specific gapmers sit **in or near the comfort band** — **37.5–50% GC** at
  E12::N3 and **50–62.5%** at E7::N3 — versus **75–81%** at the modelled codon-264 reference. The
  most-common real junction (E12::N3) is, if anything, AT-rich. So the headline chemistry caveat from §3a/§6
  is a property of that modelled position, not of the real clinical seams — exactly the red-team's F2 concern,
  resolved in the route's favour.
> ⚠ **EVERY "CLEAN" CALL IN THIS SECTION USES THE RETIRED ABOLITION ASSUMPTION AND MUST BE READ AS A
> ZERO **COUNT** AT THE ≤2-MISMATCH GAP-RESOLVED THRESHOLD, NOT AS A CLEANLINESS CALL** (§3a-quater;
> Appendix A, entry 68). The graded re-scores of this section's committed screens are
> [`junction-aso-offtarget-e7n3-graded.json`](../../modalities/junction-aso-offtarget-e7n3-graded.json) and
> [`junction-aso-offtarget-e12n3-graded.json`](../../modalities/junction-aso-offtarget-e12n3-graded.json);
> **no headline in this section moves**, because under the retired assumption those panels already read
> 0 of 5 clean. Wording here is left as written rather than silently re-touched, since this section is
> itself under a separate correction (the exon-index regeneration) that this pass does not own.

- **A predicted-clean gapmer exists at a real junction; specificity is still per-oligo.** At **E7::N3**, the
  gapmer **`5′-TACGGACAATCTGCTG-3′` (50% GC) is predicted clean on *both* screens** — **0** true cleavage
  risks under the ≤2-mismatch gap-resolved BLAST *and* **0** ≤1-mismatch off-targets in the uncapped scan
  (all five E7::N3 designs have 0 exact matches). At **E12::N3**, the GC-friendly but AT-rich/low-complexity
  seam carries a **higher 2-mismatch off-target load** (best design `GTACGGACAACATCAA`, 43.8% GC: 3 true
  cleavage risks; one design is clean at the stricter ≤1-mismatch threshold) — so no E12::N3 design is fully
  clean at ≤2 mismatches, and per-oligo selection is again decisive. The two screens reproduce the same
  stringency split seen at the modelled 200/8 (uncapped ≤1mm is cleaner than gap-resolved ≤2mm).

**The full recurrent-junction panel (now run, real, committed — 2026-07-03).** The prior draft screened only
E12::N3 and E7::N3. We have since run the full pipeline (design → gap-resolved BLAST → uncapped eval) plus the
GC-tolerant siRNA route on the remaining recurrent junctions **EWSR1 e9/e10/e13 :: NR4A3 e3**
(`junction-aso-offtarget-e{9,10,13}n3.json`, `junction-sirna-designs-e{7,9,10,12,13}n3.json`). The picture is
**more sobering than the E7::N3 result alone implied, and the honest headline is route-complementarity, not a
clean gapmer everywhere**:

| Recurrent junction | Best 16-mer gapmer (GC) | Gapmer true cleavage risks (best design, ≤2-mm gap-resolved) | Fully-clean gapmer? | siRNA designs passing all filters (min GC) |
|---|---|---|---|---|
| **E7::N3** | `TACGGACAATCTGCTG` (50%) | **0** | **yes** | 0/5 (52.6%) |
| **E9::N3** | `CCTGGTGTTGTCCGTA` (56%) | 1 | no | 0/5 (52.6%) |
| **E10::N3** | `TGATCTAGTTGTCCGT` (44%) | 1 | no | **3/5 (42.1%)** |
| **E12::N3** (most common) | `GTACGGACAACATCAA` (44%) | 3 | no | **3/5 (42.1%)** |
| **E13::N3** | `CGTGGAGTTGTCCGTA` (56%) | 7 | no | 0/5 (57.9%) |
| **E11::N3** | — | — (design step produced no output) | — | — |

Three honest readings of the panel:
- **A fully-clean 16-mer gapmer is the *exception*, not the rule.** Only **E7::N3** yields a gapmer with zero
  predicted cleavage risks; E9/E10 leave a single residual ≤2-mismatch risk, E12 three, and E13 is poor
  (seven). So the earlier "predicted-clean gapmers exist at a favorable breakpoint" stands but is **narrowed**:
  clean 16-mer gapmers are found at 1 of the 5 screened junctions. Per-oligo selection is decisive, and the
  specifiable next lever is **longer oligos (5-10-5 20-mers) and the gap-centred re-tiling** (now computed as a
  `gap_specificity_margin`; §2a/§3b.1) rather than the top-5 16-mer snapshot.
- **The siRNA route rescues the two junctions where the gapmer is weakest — including the most common one.**
  At **E10::N3 and E12::N3**, the GC-tolerant siRNA route yields **3 of 5** guides passing all filters (min GC
  42.1%), exactly where the gapmer needs careful selection or fails — whereas at E7/E9/E13 (siRNA min GC
  52.6–57.9%) it is the gapmer that carries the route. **The two modalities are genuinely complementary across
  breakpoints, and the single most common junction (E12::N3) is addressable via siRNA** even though its best
  gapmer keeps three residual risks. This is a stronger practical statement than either modality alone: the
  *panel*, not any one oligo, covers the recurrent junctions.
- **E11::N3 needs verification (integrity flag).** The design step produced no output — most likely the
  in-frame self-check (`translate(CDS).endswith(NR4A3 C-terminus)`) rejected the e11:3 exon pair at the CDS
  boundaries used, i.e. our exon indexing for EWSR1 exon 11 → NR4A3 exon 3 may not be in-frame as joined. This
  is **flagged, not hidden**; the discrepancy with the neoantigen companion (which lists exon 11 in the
  recurrent set) is a to-verify, not a claim that e11:3 does not occur. [citation to verify] for the exact e11
  boundary.

  > ⛔ **ROOT-CAUSED 2026-08-06, AND THE "most likely" ABOVE WAS WRONG.** Nothing about exon 11's
  > boundary is uncertain. Under the defective index NR4A3 resumed at CDS nt 1081, so the chimeric CDS
  > is in frame exactly when the EWSR1 cut offset ≡ 1081 ≡ 1 (mod 3). From the committed exon audit
  > ([`nr4a3-exon-audit.json`](../../modalities/nr4a3-exon-audit.json)): e7 793 ≡ 1, e9 1012 ≡ 1,
  > e10 1045 ≡ 1, e12 1294 ≡ 1, e13 1417 ≡ 1 — **and e11 1164 ≡ 0.** The junctions the pipeline
  > emitted and the one it refused are exactly what the off-by-two predicts, with no residual.
  > **A self-check firing is a diagnostic, not a footnote.** This one was the only place the defect
  > surfaced on its own, and it was recorded as an exon-boundary to-verify instead of being chased —
  > the failure CLAUDE.md §4 exists to prevent ("if you catch yourself writing *most likely* about a
  > failure, stop and go get the data"). The data was on disk the whole time and cost nothing to read.

**Reading.** Run across the *real* recurrent seams, the route is **more feasible on chemistry** than the
modelled reference implied (real junctions 37–62% GC, not 75–81%) but **less uniformly clean than E7::N3 alone
suggested**: a fully-clean 16-mer gapmer appears at 1 of 5 junctions, off-target load (not GC) is the operative
per-oligo gate, and the decisive practical point is that **gapmer + siRNA together cover the panel** — siRNA
carrying E10::N3 and the most-common E12::N3, gapmers carrying E7/E9. Honest bounds unchanged: predicted not
validated (same gap-mismatch heuristic, §3a-quater; the GPU RNase-H1 experiment of §8 would firm it), these are
the *canonical-transcript* exon junctions (a real patient's design must still come from their sequenced
breakpoint), E11::N3 is unverified, and delivery (§3c) remains the dominant gate.

> ⛔ **THIS "Reading" IS RETRACTED WITH THE SECTION.** Nothing in it stands: "real junctions
> 37–62% GC", "a fully-clean 16-mer gapmer appears at 1 of 5 junctions", "gapmer + siRNA together
> cover the panel", and the E7/E9/E10/E12/E13 attributions all derive from the retracted seam, and
> three of the five junctions' files do not exist *(⚠ superseded 2026-08-08: they DO exist, on
> `origin/modalities-cache` since 2026-07-03, carrying the retracted seam and now bannered — see
> the correction at the head of this retraction. The Reading stays retracted either way, and on
> firmer ground)*. ⚠ **The comparison it draws is the most
> dangerous part** — it tells a reader the modelled-junction chemistry problem is an artifact of
> the modelled position. That comparison is now unsupported in both directions: **the corrected
> real-junction GC values are UNKNOWN.**
>
> ✅ **They are no longer unknown (2026-08-06) — see §3a-sexies, which answers the comparison in
> BOTH directions and finds it half right.** ⚠ *Superseded, retained: "the corrected real-junction
> GC values are UNKNOWN."*

### 3a-sexies. The corrected real-junction panel — E7::N3 and E12::N3, regenerated 2026-08-06

This section replaces §3a-quinquies. It covers **two** recurrent junctions, not five: E9::N3, E10::N3 and
E13::N3 were never computed at all (retraction block, item (f)) and nothing here speaks for them.

**Construction.** The chimera is built at the **mRNA** level, not by concatenating CDSs: a fusion transcript
retains the acceptor exon whole, so the NR4A3 exon-3 bases 5′ of NR4A3's own ATG are physically in the
transcript and are the bases an oligo hybridises to immediately 3′ of the seam. Every declared exon pair is
graded first, designing nothing, in
[`junction-mrna-frame-audit.json`](../../modalities/junction-mrna-frame-audit.json); a panel is emitted only for a
row that table grades `EMITTABLE`, and only E7::N3, E9::N3, E10::N3, E12::N3 and E13::N3 qualify, with
E11::N3 refused as a frame-register mismatch and every NR4A3 exon-2 pair refused as a non-coding acceptor.

**Corrected seams.** `ACGGGCAGCAGA|ATATGCCCTGCG` (E7::N3) and `AATGGTTTGATG|ATATGCCCTGCG` (E12::N3). The
shared right-hand 12-mer is the same acceptor exon in both, which is a consequence of the shared acceptor and
**not** corroboration — the lesson of the retracted section is that agreement is evidence only between
constructions that can fail independently, and these two cannot. The cross-check that *does* count is the
live-Ensembl / committed-cache agreement in retraction-block item (e).

| | Modelled codon-264 reference (§3a) | **E7::N3 (corrected)** | **E12::N3 (corrected)** |
|---|---|---|---|
| Gapmer GC range, 5 fusion-specific designs | **75.0–81.2%** | **50.0–56.2%** | **37.5–43.8%** |
| Gap-resolved ≤2-mismatch BLAST — designs with zero true cleavage risk | 0 of 5 | **0 of 5** | **0 of 5** |
| …lowest true-cleavage count over the 5 designs | — | **12** (`GGGCATATTCTGCTGC`) | **8** (`GGGCATATCATCAAAC`) |
| Uncapped 186,185-transcript scan — designs with zero exact off-targets | — | **5 of 5** | **5 of 5** |
| …designs with zero ≤1-mismatch off-targets | 0 of 5 | **0 of 5** | **0 of 5** |
| …lowest ≤1-mismatch count | — | **3** | **1** |

Sources: [`junction-aso-designs-e7n3.json`](../../modalities/junction-aso-designs-e7n3.json),
[`junction-aso-offtarget-e7n3.json`](../../modalities/junction-aso-offtarget-e7n3.json),
[`aso-insilico-evaluation-e7n3.json`](../../modalities/aso-insilico-evaluation-e7n3.json) and the `-e12n3`
counterparts.

**Two readings, and they point in opposite directions — which is why the retracted section's single headline
was wrong even in shape.**

- **The GC "chemistry problem" IS substantially a property of the modelled junction position.** At both real
  seams the fusion-specific gapmers sit in or near the standard comfort band (37.5–56.2%) against 75.0–81.2%
  at the modelled codon-264 reference, and the most common junction (E12::N3) is the AT-rich one. The
  direction the retracted section claimed survives its own retraction — but on different numbers, from a
  different seam, so it is a new reading and not a restored one.
- **Predicted specificity does NOT improve, and the retracted "clean gapmer at E7::N3" is contradicted.**
  Under the corrected seam **no design at either junction is free of gap-spanning ≤2-mismatch near-matches**
  (lowest counts 12 and 8), and **no design is free of ≤1-mismatch off-targets** in the uncapped scan (lowest
  3 and 1). What does hold at both junctions is that **all ten designs have zero exact off-targets**. So the
  operative per-oligo gate is off-target load, not GC — the same conclusion the retracted section reached,
  reached now from data that supports it rather than from a seam no patient carries.

**Honest bounds.** These are predicted gap-mismatch and near-match counts from sequence, on canonical
transcripts, using the same heuristic as §3a-quater: predicted specificity, not measured knockdown and not
measured sparing of either parent transcript. A real patient's design must still come from their own sequenced
breakpoint; which exon pair a given patient carries is not decidable from exon structure and is not decided
here. Nothing in this section addresses potency, delivery, tolerability or clinical use, and delivery (§3c)
remains the dominant gate for the modality. The specifiable next lever is unchanged and is now better
motivated: **longer oligos (5-10-5 20-mers) with gap-centred re-tiling**, since the residual liabilities are
gap-spanning near-matches rather than GC.

### 3a-septies. The pan-partner atlas — every NR4A3 fusion, not just EWSR1 (real, committed — 2026-08-12)

Everything above this line addresses **one** 5′ partner. EMC is not defined by EWSR1; it is defined by
**NR4A3 rearrangement to a variable partner** — EWSR1 in the large majority, *TAF15* in a substantial
minority, and *TCF12*/*TFG*/*FUS* rarely [Panagopoulos]. Until now the design lane could not address
any partner but EWSR1, for no better reason than a hard-coded gene symbol, and that exclusion lands on
the worst-served subgroup: every reported objective response to an antiangiogenic TKI in advanced EMC —
the only systemic class with activity here — has occurred in a **non-TAF15** patient, with the TAF15 arm
at 0 events across 3–5 patients. That contrast, its zero-event ceiling and the primary authors' own hedge
that the fusion is a *surrogate* rather than a mechanism are owned by
[`emc-fusion-partner-pooling.json`](../fusion-partner/emc-fusion-partner-pooling.json) and are not restated here. What
follows from it for *this* paper is only this: **the partner-defined subgroup with the fewest options was
the one the design code excluded.**

[`nr4a3_fusion_atlas.py`](../../modalities/nr4a3_fusion_atlas.py) →
[`nr4a3-fusion-junction-atlas.json`](../../modalities/nr4a3-fusion-junction-atlas.json) closes that, at $0,
offline, from the committed Ensembl transcript cache. It grades **231 donor-exon × NR4A3-acceptor-exon
pairs across all five reported partners** — every pair, refusals included — and emits junction-spanning
gapmer panels for the rows it grades `EMITTABLE`.

| | EWSR1 | TAF15 | TCF12 | FUS | TFG |
|---|---|---|---|---|---|
| pairs graded | 51 | 48 | 63 | 45 | 24 |
| `EMITTABLE` junctions | 8 | 8 | 8 | 8 | 6 |
| junctions yielding ≥1 fusion-specific design | **8** | **8** | **8** | **8** | **6** |
| GC range across those designs | 37.5–75.0% | 31.2–68.8% | 25.0–56.2% | 31.2–62.5% | 25.0–50.0% |
| provenance gate available | graded exon audit | construct-inputs self-checks only | " | " | " |

⚠ *Superseded, retained: **207 pairs across four partners**, `EMITTABLE` **32**, and the statement
in `PARTNER_ABSENCE_HINTS` that TFG could not be scored. All were true until 2026-08-12, when a CI
fetch added TFG's transcript model (ENST00000240851) to `emc-construct-inputs.json` and the atlas
picked it up on the next run. Nothing was recomputed differently; a partner that had been named as
unscoreable became scoreable, which is exactly what naming it rather than dropping it was for.*

**Three readings, and the third is the one worth the paper.**

⚠ *Superseded, retained, and it recurs three times below: **20 of 32** unscreened. The denominator
moved from 32 to 38 when TFG entered the atlas on 2026-08-12; the twelve screened junctions did not
change, so the unscreened residual is 26 of 38.*

**(i) Designability is not the constraint.** All **38** frame-compatible junctions yield at least one
gapmer that is junction-spanning and a perfect complement of no parent transcript, at GC values mostly
inside the standard comfort band. The modality's difficulty in EMC is not finding sequences.

**(ii) The generalisation reproduces the established EWSR1 result rather than moving it.** Restricted to
this repository's declared EWSR1 breakpoint window, the `EMITTABLE` set is exactly **e7, e9, e10, e12,
e13**, with **e11 refused** as a frame-register mismatch — the corrected 2026-08-06 result, re-derived by
donor-generic code that never mentions EWSR1. Three further EWSR1 rows (e1, e4, e15) are frame-compatible
and sit *outside* the declared window; they are reported as arithmetic, not as clinical breakpoints.

**(iii) ⭐ One oligo can be fusion-exclusive at three different partners' junctions at once.** The
16-mer **`5′-GGGCATATCATCAAAC-3′`** (GC 43.8%, gap-centred with a gap-level margin of 3) splits **8 + 8**
across the seam of **EWSR1 e12::NR4A3 e3**, **TAF15 e11::NR4A3 e3** *and* **FUS e10::NR4A3 e3**, and
occurs in **none** of the five wild-type parent transcripts. The mechanism is measured rather than
inferred: the three donors are **identical over the 8 bases immediately 5′ of their breakpoints**
(`TGGTTTGATG`) — TAF15 and FUS are in fact identical over the whole 12-nt stored window — which is long
enough to supply the entire donor-side contribution at all three seams. ⚠ *Superseded, retained: "the 8
bases immediately 5′ of their breakpoints (`GTTTGATG`)."* Eight is the donor contribution of **one** of
the five designs; they range 6 to 10, so an 8-base run would not have covered two of the five the
sentence generalised over. The measured three-way run is ≥10. Nine
multi-partner designs exist in total: **five** cover this same three-partner set (differing only in how
the 16-mer is registered across the seam, 6+10 through 10+6) and four cover two partners. Of the five,
`GGGCATATCATCAAAC` is the one with the largest gap-level margin, which is why it is the one named.

**Why this is the interesting number, and why it cuts both ways.** FET-family paralogy is the reason the
per-oligo specificity screen had to be widened from two parents to all five — a design against one
partner's seam *can* be a perfect complement of another partner's wild-type transcript, and only a screen
that knows about every partner can see it. The same identity that creates that liability creates the
coverage: it is one sequence property, read twice. A reader must be able to see both from the artifact,
and both are in it.

**⭐ And the mechanism has a negative control that the atlas supplies for free — it came out right.** If
the coverage really is FET-family paralogy, then the one partner here that is **not** a FET protein
should be excluded from it. **TCF12 appears in no exact multi-partner set at all** — every one of the
nine is drawn from EWSR1, TAF15 and FUS. TCF12 reaches only the weaker gap-intact category, where a match
is tolerated mismatches in the wings. The prediction was not designed for: partner membership of the
coverage sets was never a criterion in the ranking, and TCF12 was in the panel because it is a reported
EMC partner, not because it was chosen as a control.

**What this changes about the deliverable.** §3b.4 says the deployable artifact is a *panel* keyed to a
sequenced breakpoint. That remains true and is now quantified — but it is no longer the only shape
available. At one junction position, a **single stock reagent** addresses the commonest EWSR1 junction and
the TAF15 and FUS equivalents together, which is a materially different manufacturing and regulatory
proposition for an ultra-rare disease than *n* bespoke oligos.

**Honest bounds, and they are firm.**

- **Frame-compatible is not clinically reported.** This enumerates an arithmetic property of exon
  structure. No partner-and-exon-resolved patient series exists here, so which exon pair a given patient
  carries is not decidable from this table. The three-partner result reads: *if* a TAF15 patient's
  breakpoint is at TAF15 exon 11 and a FUS patient's at FUS exon 10 — the positions whose donor sequence
  is identical to EWSR1 exon 12's — then one oligo serves all three. Whether patients carry those exons is
  a clinical observation nobody here has made.
- **The provenance gate is weaker for the new partners, and that is disclosed per gene.**
  [`nr4a3-exon-audit.json`](../../modalities/nr4a3-exon-audit.json) grades NR4A3 and EWSR1 only — the two
  genes the 2026-08-06 off-by-two correction was derived against. For TAF15, TCF12 and FUS that gate
  cannot run; what stands behind their seams is the weaker one (the transcript cache's own recorded
  self-checks plus three sequence self-checks). Every partner row carries which gate ran.
- ✅ **The transcriptome screen HAS now run at the two non-EWSR1 junctions the coverage result turns on
  — see §3a-octies.** ⚠ *Superseded, retained: "The gap-resolved BLAST and uncapped 186,185-transcript
  screens … have **not** been run on the TAF15/TCF12/FUS panels … Until they land, no statement about
  off-target load at a non-EWSR1 junction is available, in either direction."* That was true when
  written and is now closed for TAF15 e11 and FUS e10. It remains true for the other
  **20** emittable junctions, none of which has been screened.
- **TFG is a reported EMC partner with no transcript model in this repository**, so it is absent from the
  atlas and named as absent — by the loader, at run time, rather than by a hard-coded note. ⚠ That
  distinction is the fix, not pedantry: the first version of this asserted TFG's absence in a constant,
  which would have gone on printing "absent" after the fetch that added it, because nothing checked. The
  fetch is now wired (`emc_fet_construct_designs.py --refresh`, CI, symbol-resolved at Ensembl with no
  invented accession) and nothing else is missing; until it runs, TFG has no designs here in either
  direction.
- Nothing here addresses potency, knockdown, delivery, tolerability, safety or clinical use.

### 3a-octies. The first transcriptome screens at a non-EWSR1 junction — and the three-partner oligo screened independently at each (real, committed — 2026-08-12)

The pan-partner atlas is sequence arithmetic. This section is the network-bound screen that had never
been run outside EWSR1: the full pipeline (design → gap-resolved BLAST vs human RefSeq RNA → uncapped
186,185-transcript evaluation) executed at **TAF15 e11::NR4A3 e3** and **FUS e10::NR4A3 e3**, alongside
**EWSR1 e12** and **e7** re-run in the same job.

**The design panels at the three junctions came back identical, oligo for oligo.** All three emit the
same five gapmers, headed by `GGGCATATCATCAAAC`.

⛔ **AND THE INDEPENDENCE THIS AGREEMENT SUPPORTS IS NARROWER THAN FIRST WRITTEN — THE CORRECTION IS
RECORDED BECAUSE THE OVER-CLAIM WAS THE RETRACTION'S OWN ERROR REPEATED.** ⚠ *Superseded, retained:*
"reproduced by **a different code path** — the per-junction CI design-and-screen pipeline, which knows
nothing of the atlas and builds each chimera independently." That is false.
[`nr4a3_fusion_atlas.py`](../../modalities/nr4a3_fusion_atlas.py) **imports `junction_aso`** and calls
`transcript_model`, `mrna_junction_generic`, `grade_junction` and `design` — the same four functions the
CI workflow invokes. Seam construction, frame grading and tiling are **shared code and cannot fail
independently**. Two artifacts agreeing because one implementation produced both is precisely what the
2026-08-06 retraction was: E7::N3 and E12::N3 agreed, and the agreement was read as corroboration when a
single defect had produced both.

**What is genuinely independent is the transcript acquisition, and that is the check that counts here.**
The atlas was built offline from the committed 2026-08-09 cache; the CI run read Ensembl live and
recorded `ensembl+cache_agreed` for TAF15, FUS and NR4A3 — two separate acquisitions of the transcript
model, agreeing field-for-field. By this manuscript's own standard (§3a-sexies) that is the whole test,
and it is passed. It is not a second implementation of the design logic, and this paper must not claim
one.

| design | GC | gap-resolved BLAST: true cleavage risks | uncapped: exact | uncapped: ≤1 mm |
|---|---|---|---|---|
| **`GGGCATATCATCAAAC`** | **43.8%** | **8** | **0** | **1** |
| `AGGGCATATCATCAAA` | 37.5% | 13 | 0 | 2 |
| `CAGGGCATATCATCAA` | 43.8% | 17 | 0 | 2 |
| `GCATATCATCAAACCA` | 37.5% | 46 | 0 | 22 |
| `GGCATATCATCAAACC` | 43.8% | 50 | 0 | 7 |

Identical at EWSR1 e12, TAF15 e11 and FUS e10 — sources
[`junction-aso-offtarget-taf15e11n3.json`](../../modalities/junction-aso-offtarget-taf15e11n3.json),
[`-fuse10n3`](../../modalities/junction-aso-offtarget-fuse10n3.json),
[`aso-insilico-evaluation-taf15e11n3.json`](../../modalities/aso-insilico-evaluation-taf15e11n3.json) and
counterparts, on branch `modalities-cache`.

**Four readings.**

**(i) The multi-partner design is the cleanest of the FET-junction designs.** `GGGCATATCATCAAAC` carries
**8** predicted true cleavage risks against 13–50 for the other four at the same junction, and against
**12–50** at E7::N3 (§3a-sexies). ⚠ It is **not** the cleanest in the paper — TCF12 designs reach 1
(§3a-nonies) — and the counts here are right-censored wherever they read 50. Its single ≤1-mismatch off-target in the uncapped scan is one histone transcript
(`NM_012274.2`). Nothing forced this: coverage and off-target load are independent properties, and the
oligo that reaches three partners could easily have been the dirtiest. It is the cleanest of the twenty
screened.

**(ii) The conclusion does not change, and that is the honest headline: 0 of 5 clean at every junction.**
No design at any of the four junctions is free of gap-spanning near-matches. Extending to new partners
did not find an escape from the finding §3a-sexies already reported for EWSR1 — it reproduced it. What
the screens support is a **rank ordering** for a wet-lab specificity assay, not a clean call.

**(iii) The parent-set correction was live, and it changed nothing here — which is a measurement.**
The screen now excludes the *donor's own* transcript rather than always EWSR1's (§3a-septies). At these
junctions **`n_parent_or_intended_hits` is 0 for every oligo**, so the widened and re-pointed parent set
neither hid a hit nor manufactured one. ⚠ **For two of the five that zero is right-censored and must not
be read as a measurement**: `GGCATATCATCAAACC` and `GCATATCATCAAACCA` each returned exactly 50
near-matches, which is the BLAST hit-list cap, so a parent hit ranking below the 50th would be invisible.
The claim holds for the three uncensored designs and is an absent reading for the other two. That is worth stating precisely because it could have gone the
other way: the fix was made on the reasoning that a stale parent set errs in both directions at once, and
at these junctions the error would have been zero. ⚠ The accession arm of that exclusion is inert for
TAF15 and FUS (no verified RefSeq accession is held here), so the exclusion rested on name matching
alone; every artifact records which arms were live.

**(iv) The new partners' seams now have two independent acquisitions.** The CI run recorded
`ensembl+cache_agreed` for TAF15, FUS **and** NR4A3 — a live Ensembl read that agreed field-for-field
with the committed 2026-08-09 cache the atlas was built from. The atlas's seams were cache-only when
written; they are not now.

### 3a-nonies. TCF12 — the partner excluded from pan-FET coverage has the best specificity (real, committed — 2026-08-12)

All **eight** emittable TCF12 junctions were then screened, completing partner coverage. TCF12 is the
one non-FET donor in the panel, and §3a-septies' negative control already showed it is excluded from
every exact multi-partner set. The screens show it is compensated on the other axis.

| junction | designs clean (gap-resolved) | lowest true cleavage risks | designs with 0 ≤1-mm off-targets (uncapped) |
|---|---|---|---|
| **TCF12 e7** | 0 of the **4 successfully screened** | **1** | **4 of 5** |
| TCF12 e9 | 0 of 5 | 2 | 2 of 5 |
| TCF12 e11 | 0 of 5 | 3 | 1 of 5 |
| TCF12 e3 | 0 of 5 | 4 | — |
| TCF12 e17 / e13 / e19 / e5 | 0 of 5 (e19: of 4) | 7 / 10 / 10 / 14 | — |
| *best across EWSR1, TAF15, FUS* | *0 of 5* | *8* | *0 of 5* |

**(i) TCF12 e7 is the strongest junction on the uncapped screen.** Four of its five designs carry
**zero ≤1-mismatch off-targets** across 186,185 transcripts — the joint-highest count in the corpus.
⚠ *Superseded, retained: "the first time any design in this program has reached zero on the uncapped
screen; every junction before this returned `n_candidates_zero_offtarget = 0`."* Both halves were false.
The modelled 200/8 breakpoint reached **4 of 5** and is reported doing so in §3a-quater, and **seven of
the eight** TCF12 junctions carry at least one such design (e7 4, e9 2, e19 2, e3/e11/e13/e17 1 each,
e5 0). What is true is narrower and is what the table now says.

**⛔ (ii) And this paper's own methodology forbids calling them clean.** The gap-resolved BLAST — the
wider test, which admits 2-mismatch hits the ≤1-mismatch cutoff structurally cannot see (§3a-quater) —
still returns **1–2 predicted true cleavage risks** for those same designs. This is exactly the
divergence red-team F5 recorded at the 200/8 breakpoint, and the resolution is the one already adopted
there: **the wider screen is the defensible one, so TCF12 e7 is 0 of 4 clean, not 4 of 5.** ⚠ One of its
five BLAST queries failed, which is why the denominator is 4 and why it is written as *"of the
successfully screened"* rather than *"of 5"*.

**(iii) What survives is a comparative statement, and it is still worth having.** TCF12 junctions carry
**lower predicted off-target load than any FET-partner junction** — a best of 1 predicted cleavage risk
against a best of 8 across EWSR1, TAF15 and FUS. So the partner that cannot share the pan-FET reagent is
the partner whose own designs look best, which is a genuine trade-off rather than a uniform ranking:
**breadth and per-oligo specificity point at different partners.**

**(iv) The parent exclusion fired for the first time.** `n_parent_or_intended_hits` is non-zero at TCF12
**e3, e5 and e19** — four hits across three junctions — and was zero at every FET junction: the first
hits classified as parent rather than off-target anywhere in the program. ⚠ For TCF12 the accession arm of that exclusion is inert (no verified
RefSeq accession is held here), so this rested on name matching alone, and the artifacts record it.

**Bounds, unchanged in kind.** Predicted, sequence-level, canonical transcripts, under the same
gap-mismatch heuristic the paper reports as retired for clean calls. **All four partners are now
screened at 12 junctions; the other 26 emittable junctions are not**, and no **exon-resolved** TCF12 breakpoint is
available — TCF12::NR4A3 fusions are reported in patients (PMID 11156374; PMID 12598313, TCF12-TEC in 1
of 10 EMCs) but not at the exon resolution these designs require. Nothing here addresses potency, knockdown,
delivery, tolerability or clinical use, and the conditional in §3a-septies stands: this speaks to TAF15
and FUS patients only if their breakpoints fall at the homologous exons, which nobody here has shown.

### 3b. What is specifiable now, without any GPU

All of the following are CPU-only and need no new GPU/compute run; they are specified, not executed, in
this draft:

1. **Expanded tiling, with a gap-centred specificity rule — gap-level margin now DONE; longer-oligo tiling
   still specifiable.** The §2a fix is **implemented**: `junction_aso.py` now computes a
   **`gap_specificity_margin`** (junction-unique bases *inside* the 6-nt catalytic gap on the shorter side) and
   a `gap_centered` flag, and ranks by it — the operative discriminator, retiring the overstating oligo-wide
   `specificity_margin` (committed in every real-junction design JSON). What remains specifiable (not yet run)
   is the **wider-window, multi-length tiling** (14–20-mers, both 5-6-5 and 5-10-5), which the corrected
   panels motivate directly: since **no** 16-mer gapmer at any screened junction is predicted clean, a
   5-10-5 20-mer sweep is the most promising remaining lever on off-target load.
   ⚠ *Superseded, retained: "to convert the 1–3-residual-risk junctions (E9/E10/E12) into clean designs."*
   Those residual-risk figures came from the retracted panel; E9 and E10 were never computed at the
   corrected seam, and corrected E12's lowest load is 8, not 1–3.
2. **Genome-wide off-target complementarity screen (CPU) — DONE, and now at twelve real junctions.**
   ⚠ *This item previously carried a paragraph duplicated verbatim, the first copy truncated mid-sentence
   at "(blastn-short vs" — a text corruption, removed 2026-08-12.* The design-time check only confirms an
   oligo is not a *perfect* complement of its parent transcripts; a real specificity claim requires a
   transcriptome-wide near-match search with gap-region weighting, because RNase-H tolerates wing
   mismatches more than gap mismatches. That has been run on the modelled reference junction (poor —
   §3a-bis), the favorable modelled 200/8 junction (§3a-quater), and on **twelve real exon junctions
   across all four partners** (§3a-sexies, §3a-octies, §3a-nonies).
   ⛔ *Superseded, retained: "The real junctions are markedly more GC-favorable than the modelled
   reference and yield a predicted-clean gapmer at E7::N3."* The GC half survives; the clean-gapmer half
   is **contradicted by the corrected screen** — E7::N3's lowest predicted cleavage load is 12, and no
   design at any of the twelve junctions is predicted clean. The remaining specifiable items are the
   gap-centred re-tiling (§3b.1), the 20 unscreened frame-compatible junctions, and any additional
   patient breakpoints as they are sequenced.

   **Per-breakpoint feasibility scan — DONE (§3a-ter), and the favorable-breakpoint screens are now DONE too
   (§3a-quater).** The sensitivity sweep over 390 modelled breakpoints has been run and committed
   ([`junction-breakpoint-scan.json`](../../modalities/junction-breakpoint-scan.json)); the reference position is
   unfavorable and in-band designs exist elsewhere. Both the gap-resolved BLAST screen and the uncapped
   full-transcriptome screen have since been run on the favorable 200/8 example (§3a-quater) — so the
   remaining specifiable items are the **real exon-3 junction** designs (above) and the gap-centred re-tiling,
   not "run a screen on a favorable breakpoint."
3. **siRNA alternative (computable) — DONE for the modelled breakpoint (§3a-bis ii).** Junction-spanning
   19-mer siRNA guides have now been generated (asymmetry/end-stability/run filters); at this breakpoint 0
   of 5 pass (min GC 73.7%), so the GC-tolerant route does not rescue this junction. Seed off-target
   counting against the transcriptome remains specifiable for any breakpoint that yields in-window-GC guides.
4. **Breakpoint heterogeneity → a per-patient panel.** ⛔ *The "7 distinct in-frame junctions" citation
   below is RETRACTED at source:* [`fusion-neoantigen-retraction.json`](../../modalities/fusion-neoantigen-retraction.json)
   grades all seven — six `SEAM_NOT_PRODUCED`, one `SEAM_RELABELLED`, **zero with a reproduced NR4A3
   label**. ⚠ **The paragraph's own conclusion is unaffected and is *strengthened*, which is why it is
   kept:** designs are breakpoint-conditional and the deliverable is a panel keyed to a *sequenced*
   breakpoint. That was true when the exon enumeration was thought sound and is more obviously true now
   that it is not. What is withdrawn is the specific enumeration, not the argument it was used to
   illustrate. *Superseded, retained:* Because EMC breakpoints vary by exon usage (the
   companion neoantigen work resolved *7 distinct in-frame junctions* across EWSR1 exons 7/9/10/11/12/13 →
   predominantly NR4A3 exon 3; see [`novel-modalities.md`](../modality-census/novel-modalities.md) §3.3), the ASO sequence
   is **breakpoint-conditional**. The deployable artifact is therefore not one oligo but a *panel*:
   key each patient's design to their sequenced breakpoint, exactly as the script already supports by
   re-running on the patient transcript. The per-breakpoint scan (§3a-ter) now shows this panel is largely
   tractable — a clear majority of modelled breakpoints yield clean in-band designs — so favorability is a
   selection step, not a roadblock. This is a feature of the modality, not a bug — it mirrors the
   personalised logic the immunotherapy route reached independently.

### 3c. The honest hard part — tumour delivery (unsolved)

Oligonucleotide *design* is tractable; **delivery to an EMC tumour is not**, and this is stated plainly as
the limiting problem. Systemically administered naked gapmers distribute to liver/kidney; GalNAc
conjugation (the one solved targeting handle) is hepatocyte-directed and useless for a soft-tissue sarcoma.
Options below are **hypotheses, explicitly flagged**, not validated approaches — and they are listed in
*increasing* order of how much they depend on an unknown:

- **Local / intratumoural administration** for accessible lesions, sidestepping systemic targeting entirely
  — the only delivery hypothesis here that needs **no** EMC-specific surface marker, and therefore the most
  tractable first-in-human setting. (Promoted to the top because the receptor-targeted routes below all
  depend on an input that does not yet exist.)
- **Receptor-targeted antibody–oligonucleotide conjugate (AOC).** Couple the gapmer/siRNA to an antibody
  against a surface antigen enriched on EMC cells. The antigen previously named by extrapolation was
  **B7-H3 (CD276)** — broadly over-expressed across *many* sarcoma subtypes, but with EMC-specific expression
  **unknown**, so it was an *extrapolation from other sarcomas*, not evidence [citation to verify]. The
  unbiased surfaceome scan below now **reprioritises** it (B7-H3 is broad but non-selective) and offers a
  data-ranked alternative shortlist. An EMC immunohistochemistry / RNA-seq confirmation remains a prerequisite
  before any antigen is a real EMC delivery handle; AOC platforms exist in other indications but none is
  established for EMC.
- **Receptor-/ligand-targeted nanoparticle (LNP or polymer).** Encapsulate the oligo and decorate with a
  ligand for an EMC-enriched receptor. The specific EMC-enriched receptor is, again, the unsolved input
  [citation to verify].

**In-silico groundwork toward a *named* targeting antigen — an unbiased surfaceome scan (real, committed —
2026-07-03).** The AOC and targeted-nanoparticle routes both stall on the same missing input: *which surface
antigen is enriched on EMC cells?* Naming B7-H3 by extrapolation is weaker than naming a candidate from data.
So we ran an unbiased scan — [`emc_surfaceome_scan.py`](../../modalities/emc_surfaceome_scan.py) →
[`emc-surfaceome-scan.json`](../../modalities/emc-surfaceome-scan.json) — of the whole human surfaceome (UniProt
plasma-membrane + transmembrane/GPI, **2,820** genes; self-validated: housekeeping genes correctly excluded,
CD276 recovers as broadly expressed) ranked by expression across the **EMC-surrogate translocation-sarcoma
DepMap class** (Ewing/synovial/myxoid/…, n=76 lines), with the myxoid subset and rest-of-lineages for context.
Two useful, honestly-bounded results:
- **It replaces the B7-H3 guess with a data-ranked shortlist — and it *reprioritises* B7-H3.** CD276/B7-H3 is
  broadly expressed in the class (98% of lines) **but not selective** (enrichment vs other cancer lineages only
  **+0.14** log2TPM) — good for hitting the tumour, weak on the tumour-vs-background window. More selective
  surface antigens surface above it: **CDH11 (+3.18), FGFR1 (+1.99, and highest in the one myxoid line, 9.3
  log2TPM), GPC2 (+1.49), PTK7 (+1.24), MCAM/CD146 (+1.09), EPHB4 (+1.0)** — several with existing
  ADC/CAR/bispecific programs (GPC2, PTK7, FGFR-directed, MCAM). This is a *nameable*, prioritised targeting-arm
  shortlist for an EMC AOC, doubling as candidate antigens for the CAR-T/ADC routes.
  - ⛔ **SUPERSEDED 2026-08-09 — THE EMC-TISSUE TEST THIS BULLET SAID IT WAS WAITING FOR HAS RUN, AND
    THE SHORTLIST DID NOT SURVIVE IT.** The sentence below ("that needs the EMC lines' own data — see
    below") named the missing measurement; three EMC tissue cohorts have since been read, and **not one
    of the six antigens above is concordantly elevated in EMC tissue.** Two are concordantly *lower*, one
    of them emphatically: per-gene *t* against the comparator on the two array platforms, from
    [`emc-expression-panels.json`](../../modalities/emc-expression-panels.json) → `genome_wide_null` —
    **FGFR1 −4.54 and −12.19** (the second at signed percentile 0.03, with only 9 symbols on the whole
    array more extreme), **PTK7 −3.87 and −4.55**, **CDH11 +2.65 then −3.78** (discordant),
    **MCAM −2.65 then +1.18** (discordant), **GPC2 −0.36** (flat, one platform), **EPHB4 +0.56 and
    +1.72** (not distinguishable from the array background). **CD276/B7-H3 reads −2.55**, so the
    reprioritisation above stands but its replacement does not.
    ⚠ **The surrogate was not merely uninformative — for the two strongest cases it pointed the wrong
    way.** FGFR1 was ranked second on the strength of a single myxoid cell line at 9.3 log2TPM; in
    tumour tissue it is one of the most strongly *depleted* genes on the array. That is the
    cell-line-versus-primary-tissue gap this bullet's own "honest bounds" flagged, measured and coming
    out against the ranking.
    ⭐ **What replaces it is one antigen, not six.** **ALCAM** is concordantly elevated (**+7.01** and
    **+2.21**) — and it fails the normal-tissue exposure axis, so it is not a free win. **CSPG4** is
    elevated on one platform (**+7.42**) and flat on the other (**−0.40**) and is held open as the one
    untested lead. Full treatment, including the normal-organ comparison, is in
    [`emc-surface-target-landscape.md`](../surface-targets/emc-surface-target-landscape.md), which is that route's paper
    and the one home for these readings — **do not re-derive them here.**
    ⛔ **Consequence for §3c, stated plainly: the receptor-targeted AOC route has no named EMC antigen
    today.** That is why the local/intratumoural option is listed first there — it is now the only
    delivery hypothesis in this section that does not depend on an input the data has refused.
- **Honest bounds (stated in the JSON too).** It is a **surrogate** — DepMap *sarcoma* lines, not EMC (EMC has
  no DepMap line); the myxoid subset closest to EMC is a **single line** (anecdotal — the n=76 translocation
  class carries the signal); "enrichment" is vs other **cancer** lineages, **not normal tissue**, so the
  toxicity-relevant tumour-vs-normal window (GTEx/HPA) is the flagged next filter; and cell-line surface *mRNA*
  is a proxy for primary-tumour surface *protein*. This **names a candidate antigen; it does not confirm EMC
  surface expression** (that needs the EMC lines' own data — see below) and **does not solve delivery
  efficiency** (blood→tumour→cell→endosomal escape stays wet-lab).

**The decisive upgrade — real EMC data (now probed, real, committed — 2026-07-03).** EMC is no longer
model-less: patient-derived **USZ-EMC** [Bangerter 2022/2023] and **NCC-EMC1-C1** [Iwata 2025] exist and are
being studied. A data probe ([`emc_line_data_probe.py`](../../modalities/emc_line_data_probe.py) →
[`emc-line-data-probe.json`](../../modalities/emc-line-data-probe.json); Europe PMC full-text + NCBI GEO/SRA)
returns a nuanced verdict:
- **Neither new *cell line* has publicly deposited a transcriptome.** The USZ open-access paper states its data
  are *"available from the corresponding author on reasonable request"* (no accession); the NCC-EMC1-C1 paper
  is not open-access and its abstract carries no accession. The USZ full text mentions **EGFR** and **KIT**
  (a crude term-match — must be human-verified as positive *surface* IHC, not a pathway/drug-screen mention).
  So the richest real-EMC surface data (a full immunophenotype) sits **behind a paywall / on request**, not in
  a public dataset — a `[citation to verify]` to obtain from the papers directly.
- **A public real-EMC *tumour* dataset exists (`GSE4303`) but was tried and is UNUSABLE for this.** GSE4303
  ("Gene expression profile of EMC") is a 7-platform **two-colour cDNA-*clone* array** series (3 EMC
  samples/platform) whose values are log-ratios vs a reference pool (63% negative — *relative*, not absolute
  expression) and whose probes are clone/spot IDs without gene symbols; the cross-check
  ([`emc_gse4303_crosscheck.py`](../../modalities/emc_gse4303_crosscheck.py) → `emc-gse4303-crosscheck.json`)
  resolved **0** shortlist genes. The platform gate correctly flagged the data rather than forcing a
  meaningless ranking. **So the public-data route to real-EMC surface expression is exhausted** — the
  author-held **USZ/NCC line** data is the genuine (only) unlock.

**Net:** the sarcoma surrogate is the honest current basis; with the public tumour dataset (GSE4303) ruled
out, the real-EMC upgrade must come from the **USZ/NCC line** immunophenotype/RNA-seq if the authors deposit
or share it — which would move the §3c targeting-antigen shortlist from "surrogate" to "real EMC." This is the
highest-value delivery-directed next step.

> **Scope note — this surface-antigen work is being spun out.** Surface-antigen targeting is a *different
> thesis* from this paper's fusion-exclusivity (a surface antigen is not the fusion; its selectivity is
> tumour-vs-normal antigen distribution, not fusion sequence) and a *different, less-delivery-gated modality
> axis* (ADC / T-cell engager / CAR / radioligand, beyond the AOC arm). It therefore graduates into its own
> **target-class** manuscript, [`emc-surface-target-landscape.md`](../surface-targets/emc-surface-target-landscape.md)
> (scaffolded, gated on the real EMC surface data above) — the way the degrader paper was split from the EMC
> roadmap. This section keeps only the *delivery-arm* relevance to the ASO; the antigen landscape lives there.

No delivery claim is made; this section exists to mark delivery as the dominant risk, to **narrow the
targeting-arm unknown from "none named" to a data-ranked shortlist**, and to point at the EMC lines that could
confirm it — not to assert a solution.

### 3c-bis. Delivery is three routes with different requirements, not one gate — and only one of them needs the antigen (2026-08-12)

⛔ **THE PRECEDING SECTION IS CORRECT AND ITS SUMMARY HAS BEEN MIS-STATED — INCLUDING BY THIS
REPOSITORY'S OWN PORTFOLIO GRAPH.** §3c already lists **local/intratumoural administration first**,
explicitly because it is *"the only delivery hypothesis here that needs **no** EMC-specific surface
marker"*. Yet the route is carried in [`systems/graph/blockers.json`](../../../systems/graph/blockers.json)
under a single `BLK-DELIVERY` of kind `requires_future_technology`, retired only by a capability whose
own definition is systemic — *"a conjugate, tumour-penetrating peptide or ligand-targeted lipid
nanoparticle — OR a characterised EMC-enriched surface antigen"* — with a forecast of **2029**. A
monolithic blocker takes the hardest route's requirement and applies it to the modality. **The antigen
that the tissue data has refused (§3c, `aso-delivery-antigen.json`) is a prerequisite of exactly one of
the three routes below, and it has been gating all three.**

The retrieval record for this section is [`aso_delivery_routes.py`](../aso_delivery_routes.py) →
[`lit-targets-aso-delivery-routes.json`](./lit-targets-aso-delivery-routes.json), $0, read from corpora
already published to the `literature-cache` branch. **A record there is evidence the record exists. It
is not evidence that any route works, and none of the counts below is used to claim a gate is passed.**

| route | needs an EMC surface antigen? | what the retrieval finds | what is still unknown |
|---|---|---|---|
| **R1 · local / intratumoural** | **no** | 37 records. ⚠ Read narrowly: a 2025 review of pulmonary siRNA delivery lists *"intratumoral injections, implantable depots, inhalable aerosols, and image-guided procedures"* among localised oncology approaches and notes that direct **drug** delivery is already widely applied in liver, eye, peritoneum, breast, joint, coronary and brain disease (**PMID 41658564**) — that is a statement about localised administration generally, **not** evidence that intratumoural *oligonucleotide* dosing is established | reaches accessible lesions only — not a strategy for disseminated disease |
| **R2 · inhaled / pulmonary** | **no** | **68 records** on inhaled or intratracheal oligonucleotide delivery to lung tumours, against **684** on inhaled oligonucleotide delivery outside oncology, including repeated demonstrations of gene silencing *in tumours metastatic to the lung* | deposition and uptake in a matrix-dominated EMC nodule is untested; see the bounds below |
| **R3 · systemic receptor-targeted (AOC / ligand-NP)** | **yes** | the platform exists in other indications | **no EMC antigen survives the tissue test** (§3c) — this route, and only this route, is blocked on the missing input |

**⭐ R2 is the route this disease's own natural history points at, and nobody in this program had asked
about it.** Three readings, from three independent kinds of source, agree that EMC's distant spread is
**lung-dominant**:

1. **This repository's pooled denominator**, owned by
   [`emc-locoregional-eligibility.json`](../../modalities/emc-locoregional-eligibility.json) and not
   re-derived here: **36.3%** (94/259, Wilson 95% CI 30.7–42.3%) of localised patients develop distant
   disease across three non-overlapping series.
2. **Site, where any cohort records it.** The registry's metastatic-at-diagnosis cohort reports
   **27 lung and 2 peritoneal metastases in 29 patients**. ⚠ That is a *free-text note in one cohort*,
   not a curated field, and it is a presenting population rather than a pooled site distribution — the
   limitation is stated at source and is why this is listed as one reading among three rather than as
   the answer.
3. **An external review, retrieved rather than recalled.** A 2025 comprehensive EMC review states that
   distant metastases develop in *"around 35-45% of patients, primarily in the lungs"*, with median time
   to metastasis *"approximately 28 months"* (**PMID 41055792**). The rate agrees with (1) from a
   completely different aggregation, and the site statement is the one this repository could not compute.

⭐ **And the ~28-month median matters as much as the site does.** A delivery route needs a *window*, and
a disease whose metastases appear over years rather than weeks is one where a lung-directed strategy has
time to be applied. A large retrospective cohort separately observed a trend to better survival for
**solitary** lung metastases (**PMID 32612944**) — consistent with, though not evidence for, the premise
that lung-confined disease in EMC is a meaningful clinical category.

So the organ this modality can be delivered to *without solving targeting* is the organ this disease
goes to, on a timescale long enough to act. ⚠ **What none of these three establishes is the number that
would actually size the route**: what fraction of metastatic EMC patients are lung-**confined**. That
requires lesion-burden curation no published series provides, is recorded as open in
`emc-locoregional-eligibility.json`, and is not asserted here in either direction.

**What the retrieved record actually supports, at its true weight.** Inhaled and intratracheal
oligonucleotide delivery is not a hypothetical route: dry-powder, nebulised and nanocarrier siRNA
formulations have repeatedly produced **specific gene silencing in tumours already growing in the lung**
in animal models — *"strong and specific gene silencing activity against tumors metastasized to the
lungs"* at a 3 µg dose (**PMID 29627404**), silencing quantified histologically and separately in
airways, parenchyma **and** lung tumours (**PMID 26138669**), and increased survival treating
*established* lung metastases (**PMID 31481310**). Reviews describe the respiratory system as suited to
direct delivery by *"large surface area, rich vascularization, and anatomical accessibility"*
(**PMID 41658564**), and the formulation and barrier literature — mucociliary and cough clearance,
alveolar macrophage clearance — is mature enough to have its own reviews (**PMID 28392618**).

**⛔ And the bounds, which are wide and are the reason this is a section and not a claim.**

- **No EMC.** Not one retrieved record concerns EMC, and none concerns a sarcoma lung metastasis. Every
  result above is another tumour type in a mouse.
- **The barrier is real and untested here.** An EMC pulmonary metastasis is a **parenchymal, hypocellular,
  matrix-dominated nodule**, not airway-surface disease. Deposition, penetration from the airway lumen
  into such a nodule, cellular uptake and endosomal escape are all unaddressed by a literature count.
  ⚠ EMC's myxoid matrix is a specific reason for caution, not a generic one: this repository has already
  closed one route on the arithmetic that a modality *dosed per unit volume but delivered per cell* is
  penalised in a tumour with few cells per unit volume.
- **The models flatter the route in one direction and understate it in another, and both are recorded.**
  ⚠ Lung-metastasis models made by intravenous cell injection grow *from the vascular side*, so an inhaled
  formulation reaching the epithelial side may be **under**-estimated — stated in the source that raises
  it (**PMID 30954524**). Against that, mouse airway geometry and a single-dose murine readout flatter
  deposition relative to a human lung.
- ⭐ **CORRECTED, AND IN THE DIRECTION THAT HELPS: THE INHALED OLIGONUCLEOTIDE ROUTE HAS REACHED
  PATIENTS — REPEATEDLY, AND WITH AN ASO.** ⚠ *Superseded, retained: "Only 3 of the 68 records carry
  clinical-stage language at all … No inhaled oligonucleotide against a solid-tumour target is claimed
  here to have reached patients."* The first clause was an artifact of a partial corpus — the broad
  inhaled-delivery fetch had not published when it was written, and **52** of the retrieved
  inhaled-route records carry clinical-stage language. The second clause was true only because of its
  final six words, and stating it that way understated the route. Retrieved, and each is a distinct
  agent in a distinct indication:
  - **SPL84**, an **inhaled antisense oligonucleotide**, phase 1, 32 healthy volunteers, single
    inhaled dose across four escalating cohorts (**PMID 39500647**). ⚠ **It is a splice-switching
    (steric-block) ASO**, targeting a CFTR cryptic-exon splicing defect — *not* an RNase-H1-active
    gapmer. It establishes that an inhaled ASO can be formulated and dosed in humans; it does not
    establish that for this paper's mechanism, whose chemistry and gap requirement differ.
  - **SNS812**, *"First in Human Fully Modified siRNA"*, inhaled, phase 1 single- and multiple-ascending
    dose in healthy participants (**PMID 40116355**).
  - **MIR 19 / siR-7-EM/KK-46**, inhaled siRNA, an open-label randomised controlled multicentre
    **phase 2b-3** trial (**PMID 40028836**, NCT05783206).
  - **TRK-250**, inhaled siRNA, phase 1 in 34 **patients** with idiopathic pulmonary fibrosis
    (**PMID 37738329**).

  ⛔ **What this does and does not license.** It establishes that inhaled oligonucleotides can be
  formulated, aerosolised, dosed and tolerated **in humans** — the route is not a preclinical
  curiosity, and the pharmaceutical questions this paper cannot answer have been answered in some
  other indication by someone. It establishes **nothing** about reaching a tumour: every agent above
  targets airway epithelium, lung parenchyma or a virus in the airway, which is the compartment
  inhalation naturally reaches. **A metastatic sarcoma nodule is not that compartment**, and no
  retrieved record concerns a solid-tumour target, a sarcoma, a fusion transcript, or EMC. The gap
  between "the route works in people" and "the route reaches an EMC lung metastasis" is the whole
  remaining question, and it is untouched.
- **Silencing a reporter or a pathway gene is not silencing a fusion.** Every retrieved lung result
  targets a conventional gene. The junction-specific mechanism this paper is about has never been
  delivered by this route.

**⭐ R4 — and this is the answer to "is anyone else solving this for us?"** Partly, and in the two places
that matter most to this paper.

- **A fusion-directed siRNA has been delivered systemically to a sarcoma tumour in an animal.** Cationic
  hydrogenated detonation nanodiamonds carried an **anti-EWS-FLI1 siRNA into a Ewing sarcoma xenograft**,
  with tritium labelling used to measure biodistribution and excretion, and *"siRNA directed against
  EWS-FLI1 inhibited this oncogene expression in tumour xenografted on mice"* (**PMID 32204428**). This is
  a soft-tissue/bone sarcoma, not a liver, and the payload is fusion-directed — the two properties GalNAc
  precedent (§1a vi) does not have. ⚠ It is a mouse xenograft with a nanoparticle platform, not a
  clinical delivery solution, and it is one report.
- **⛔ AND THE EXPERIMENT §4 ASKS FOR HAS ALREADY BEEN RUN — IN A DIFFERENT RARE SARCOMA, WITH THE EXACT
  CONTROL ARCHITECTURE THIS PAPER SPECIFIES.** In solitary fibrous tumour, isogenic cell models were
  CRISPR-engineered to carry the **NAB2::STAT6** fusion, and **fusion-specific ASOs** were then evaluated
  against them, reducing fusion expression by **58%** and cell proliferation by **22%** in vitro
  (**PMID 37370737**). ⚠ **The tumour-growth reduction reported in that study belongs to its
  AAV2-CRISPR/CasRx arm, not to the ASO**, and is not claimed here. That is §4's design —
  fusion-specific ASO, engineered fusion-positive/fusion-negative isogenic pair, knockdown plus
  phenotype — executed end-to-end in a rare soft-tissue sarcoma. **It is not our result and
  we claim nothing from it**; what it establishes is that §4 is a *routine, published, executable
  protocol* rather than a speculative ask, which is the single most useful thing an outreach letter can
  say to a lab deciding whether to spend a technician-month on an ultra-rare disease.

**What follows, and it is a change in sequencing rather than a claim of progress.** The correct statement
is not *"delivery is solved"* and not *"delivery is a 2029 technology"*. It is: **two of the three
delivery routes for this modality do not depend on the input EMC lacks, one of them is matched to where
this disease actually spreads, and the paper's decisive experiment (§4) is worth running before any of
them is settled** — because a junction-ASO that cannot silence the fusion in an EMC cell is not worth
delivering by any route, and one that can is worth the delivery work. **Delivery gates the therapy. It
does not gate the experiment, and it should not have been gating the paper.**

---

## 4. The decisive experiment we ask others to run

Computation cannot establish that junction silencing kills EMC cells, nor confirm parental sparing in a
living transcriptome. The single decisive, wet-lab-doable experiment is:

**Junction-ASO vs. scrambled-control knockdown in patient-derived EMC lines.** Transfect (or free-uptake /
gymnose) the committed candidate gapmers — and a junction-spanning siRNA — into **USZ-EMC** [Bangerter] and
**NCC-EMC** [Iwata], against a scrambled/mismatch control matched for length and GC. Read out:

1. **On-target knockdown** of the fusion transcript (junction-spanning qPCR / RNA-seq across the breakpoint)
   and of fusion protein.
2. **Specificity — the crux:** wild-type *EWSR1* and wild-type *NR4A3* transcripts must be **spared**
   (allele/exon-resolved or junction-discriminating assays), confirming the oligo silences only the chimera.
3. **Phenotype:** viability/proliferation/apoptosis, to test whether the cells are addicted to the fusion
   transcript.

**The controls matter as much as the readouts — and an EMC line alone cannot prove fusion-exclusivity.** A
scrambled control tests only sequence-independent toxicity; it does *not* test fusion-vs-wildtype
discrimination. Two further controls are required to make the claim. (a) **A setting where wild-type NR4A3 is
abundantly expressed** — in EMC cells wild-type *NR4A3* may be minimally expressed, so "sparing" cannot be
demonstrated where the wild-type transcript is near-absent; the discriminating test is a **fusion-negative
cell engineered to express the fusion** (or an isogenic fusion knock-in/parental pair) carrying *both* the
chimera and abundant wild-type *NR4A3*/*EWSR1*. (b) **Single-parent-targeting positive controls** — ASOs
against wild-type *EWSR1* or *NR4A3* alone — to prove the assays can detect wild-type knockdown when it
occurs, so that "spared" is a real negative and not an insensitive assay. The phenotype arm likewise needs a
**fusion-negative line** to separate fusion-knockdown lethality from generic oligo toxicity. With these
controls the experiment converts five sequences and a mechanism into evidence; without them it can show
on-target knockdown and EMC-cell killing but cannot *prove* the wild-type transcripts are spared. It needs no
new molecule beyond synthesising the listed oligos and the engineered/isogenic models above.

**⭐ One reagent worth prioritising, and why it is the highest-information single oligo in the paper.**
If only a handful of sequences can be synthesised, **`5′-GGGCATATCATCAAAC-3′`** (§3a-septies) is the one
to make first. It is gap-centred, sits at 43.8% GC, and is predicted junction-spanning and
parent-sparing at **EWSR1 e12::NR4A3 e3, TAF15 e11::NR4A3 e3 and FUS e10::NR4A3 e3** simultaneously. That
makes it a single experiment that tests the paper's central mechanism *and* its most surprising
structural prediction at once: if it silences the fusion in an EWSR1 e12 line, the mechanism holds; if it
also silences a TAF15 or FUS fusion at the homologous junction, the shared-donor-run prediction holds and
a stock reagent — rather than a bespoke panel — becomes the realistic deliverable for an ultra-rare
disease. **If it fails at one partner and works at another, that is informative too**, and it is exactly
the discriminating result no amount of further sequence analysis here can produce. ⚠ The multi-partner
prediction assumes patients carry breakpoints at those homologous exons, which is not established
(§3a-septies bounds); a line carrying a different TAF15 exon tests nothing about this oligo.

**⭐ This experiment is a published protocol, not a speculative ask — say so in the letter.** The same
design (fusion-specific ASO, CRISPR-engineered isogenic fusion-positive/negative pair, knockdown plus
growth readout) was executed in **solitary fibrous tumour** against **NAB2::STAT6**, giving 58% reduction
in fusion expression and a 22% reduction in proliferation in vitro (**PMID 37370737**, §3c-bis; the
tumour-growth reduction in that study is attributable to its CRISPR/CasRx arm) — in a rare soft-tissue
sarcoma, with the very controls the red-team required here. A lab weighing a technician-month on an
ultra-rare disease is being asked to repeat a routine protocol on a new fusion, not to invent one.

**Named recipients — the outreach ask (preprint-stage action).** This is no longer an abstract "someone should
run it": two groups now hold patient-derived EMC lines and screen drugs on them — the **USZ / University
Hospital Zurich** group [Bangerter 2022/2023, USZ-EMC] and the **NCC / National Cancer Center Japan** group
[Iwata 2025, NCC-EMC1-C1]. When the preprint posts, the concrete outreach is to those two labs with **two
asks**: (1) the make-or-break **junction-knockdown + parental-sparing + phenotype** experiment above; and
(2) — the delivery-directed one — **their EMC lines' surface immunophenotype / RNA-seq**, which is currently
*"available on request"* (USZ) or paywalled (NCC) and would replace the §3c DepMap *surrogate* with real-EMC
surface data, validating (or refuting) the surfaceome-scan targeting-antigen shortlist. Ask (2) costs the
authors almost nothing (data they already hold) and directly de-risks the delivery gate — the highest
value-per-effort outreach item. *(The in-silico partial substitute — cross-checking the shortlist against the
public EMC-tumour microarray `GSE4303` — is done, §3c; author-held line data is the stronger version.)*

---

## 5. Selectivity and safety

- **Fusion-exclusive by sequence — and the discrimination lives in the catalytic gap.** The active oligo
  spans the breakpoint; selectivity is enforced by base-pairing, not by protein conformation. The precise
  (and limiting) condition is that the **6-nt DNA gap** straddle the junction with junction-unique bases on
  each side: "a parent matches only one wing" is necessary but not sufficient (a parent matching the full gap
  plus a flank could still be cleaved). This is why the gap-mismatch-resolved off-target screen, not the
  oligo-wide specificity margin, is the operative filter (§2a, §3a-quater).
- **Spares wild-type NR4A3 — a selectivity property, and it is claimed as nothing more.** Because the
  junction is absent from wild-type *NR4A3*, a design that engages only the junction leaves the wild-type
  transcript intact. What that buys is fusion-versus-wild-type discrimination, which the LBD degrader
  cannot offer; it is **not** a safety advantage over the degrader, because no evidence here establishes
  that losing wild-type NR4A3 alone is harmful.
  ⚠ *Superseded, retained (2026-08-14): "**Spares wild-type NR4A3 — and therefore avoids the
  tumour-suppressor liability the degrader carries.** This is the key safety advantage over the LBD
  degrader … side-stepping the AML risk of combined NR4A1/NR4A3 loss [Mullican] and the HCC/breast/lymphoma
  tumour-suppressor roles of NR4A3 [Safe & Karki]." Grounds and the manuscript edit:
  [Appendix B.10](#appendix-b10--the-wild-type-nr4a3-liability-argument-withdrawn-from-the-introduction-2026-08-14-0).*
- **Spares wild-type EWSR1.** EWSR1 is a broadly expressed FET-family gene with essential functions; a
  junction oligo leaves the wild-type *EWSR1* transcript intact, matching only one wing.
- **Residual risks remain and must be tested, not assumed away:** sequence-based off-target hybridisation
  elsewhere in the transcriptome (the §3b CPU screen is the in-silico filter; only the wet-lab experiment
  is proof), and chemistry-class / phosphorothioate effects (hepatotoxicity, complement, platelet effects)
  that are generic to oligonucleotide drugs [Crooke et al. 2021]. Predicted specificity is a screen, not a
  guarantee (§6).

---

## 6. Limitations

- **GC-rich chemistry.** The modelled junction yields 75–81% GC gapmers — outside the comfort zone; high Tm
  and self-structure risk would need chemistry tuning, an alternative register, or the siRNA route (§2b).
  This is a real, committed finding, not a hypothetical.
- **Poor predicted specificity at the modelled reference breakpoint.** The BLAST off-target screen (§3a-bis i)
  found **0 of the 4 successfully screened** gapmers free of gap-spanning near-matches (the 5th BLAST query
  failed), and the GC-tolerant siRNA route did not rescue it (0 of 5 guides pass; min GC 73.7%, §3a-bis ii).
  Two honest qualifiers on the BLAST number: it is over-called (HITLIST capped at 50, low-complexity filter
  off, on a low-complexity GC-rich window), **and** — unlike the favorable-breakpoint run — it was scored
  coverage-only, *not* gap-mismatch-resolved, so its "0 clean" is an upper-bound-on-risk count not strictly
  comparable to the §3a-quater 200/8 BLAST screen. The **load-bearing** negative is therefore the
  **uncapped, true-count** full-transcriptome re-screen (§3a-bis iii): all five gapmers have 0 exact matches
  and **8–95 ≤1-mismatch** off-targets, `n_candidates_zero_offtarget = 0`. On that defensible footing the
  reference junction is specificity-poor. That same evaluation also flags a large siRNA-seed off-target load
  (~21k–119k seed sites; version-dependent point estimates) for the GC-rich seam.
- **Breakpoint-conditional — a tractable selection step, not a roadblock.** Feasibility (chemistry GC,
  siRNA GC, predicted specificity) is a property of the *junction sequence*, not of the modality, and the
  modelled reference junction is genuinely unfavorable. The per-breakpoint scan (§3a-ter) shows
  **243 of 390 modelled breakpoints (62%) pass a GC/complexity/parent-substring triage** and yield in-band
  designs — so junction-favorability is a *selectable* criterion, not a fatal flaw. But the reassurance is
  bounded harder than the bare "62%" implies: (i) the 390 are an **arbitrary codon-space grid** with
  hand-chosen thresholds, so 62% is an **upper bound on *designable* positions, not a real-patient breakpoint
  frequency**; (ii) "favorable" requires only that a triage-passing in-band design *exists* — and triage is
  **not** the off-target screen (the 200/8 worked example shows the scan's own in-band pick failing the BLAST
  screen, §3a-ter/§3a-quater). ✅ **Caveat (iii) — that the screens had only run on modelled positions — is CLOSED.**
  ⚠ *Superseded, retained, and it was true only of the retracted panels: "Those runs used a seam graded
  `SEAM_NOT_PRODUCED`, so every screen in this manuscript has still only run on modelled positions."*
  Twelve real exon junctions across four partners have since been screened (§3a-sexies, §3a-octies,
  §3a-nonies) at seams graded frame-compatible and verified against two independent transcript
  acquisitions. ⚠ *Superseded, retained: "**The residual is different and smaller: 26 of the 38
  frame-compatible junctions remain unscreened.**"* **All 38 are now screened and orientation-filtered
  (Appendix B.3, B.4), so the coverage residual is zero.** What survives is the part that no amount of
  coverage closes: every clinical design must still be re-derived from the patient's *sequenced* fusion
  transcript.
- **Delivery unsolved — and it is three routes, not one gate (§3c-bis).** No validated tumour-delivery
  route for EMC exists, and this remains the dominant risk for the whole modality. What is corrected is
  the *shape* of the risk, not its size: the missing EMC surface antigen gates the **systemic
  receptor-targeted** route only, while local/intratumoural and inhaled/pulmonary administration need no
  antigen. Inhaled oligonucleotide delivery producing gene silencing in lung tumours is an active
  preclinical field in **other** tumour types, in **animals**; no retrieved record concerns EMC, a
  sarcoma lung metastasis, a fusion target, or a patient, and an EMC pulmonary metastasis is a
  hypocellular matrix-dominated parenchymal nodule whose penetration and uptake properties are untested.
  **This changes what should be attempted first. It does not move the modality closer to a patient.**
- **The pan-partner atlas is exon arithmetic, not clinical epidemiology (§3a-septies).** It grades what
  is frame-compatible; no partner-and-exon-resolved patient series exists here, so the three-partner
  oligo result is conditional on breakpoints falling at homologous exons — an assumption nobody in this
  program has tested. ⚠ *Superseded, retained: "The transcriptome-wide off-target screens have **not**
  been run on the TAF15/TCF12/FUS panels, so nothing about their off-target load is known in either
  direction."* They have (§3a-octies, §3a-nonies): TAF15 e11, FUS e10 and all eight TCF12 junctions are
  screened. ⚠ *Superseded in turn, retained: "What remains true is that **26 of 38 frame-compatible
  junctions are unscreened**" — all 38 are screened as of Appendix B.4.* What remains true is that
  the provenance gate behind the three non-EWSR1 partners' transcript models is the weaker of the two
  available, and that TFG, the fifth partner, has no independent exon audit at all.
- **Knockdown, not knockout.** ASO/siRNA reduce transcript; they do not eliminate the gene or guarantee
  durable, complete loss of fusion protein. Depth and duration of knockdown are empirical.
- **⛔ THE PAPER NO LONGER CALLS ANY DESIGN "PREDICTED CLEAN", AND THE HEURISTIC THAT ALLOWED IT WAS NOT
  CONSERVATIVE.** The favorable-breakpoint calls assumed any mismatch inside the 6-nt gap abolishes RNase-H
  cleavage. **PMID 23963702** measures ~5-fold discrimination for an unmodified RNase-H-active ASO (>100-fold
  only with chemistry these designs lack), and **PMID 7567450** reports that 16mers — the length used here —
  "did not discriminate efficiently"; so the assumption was *optimistic*, not conservative, and against the
  length-matched source it fails outright. §3a-quater now reports a **residual predicted cleavage load** under
  both bounds, on which **0 of 5** designs at that modelled seam reach zero. ⚠ *That figure is about the
  modelled 200/8 seam and must not be read across the corpus: over the 38 real junctions, nine designs
  reach zero residual load under both bounds AND carry no hybridisable near-match over a complete hit
  list (Appendix B.4). The heading's claim that the paper "no longer calls any design predicted clean"
  is therefore superseded — what it must not do, and does not, is call a design clean on a truncated hit
  list.* What the screens support at every other junction is a **rank ordering** of
  candidates for a wet-lab specificity assay. ⚠ A ranking is also a weaker instrument than a clean call in a
  way that matters downstream: it cannot say the best design's residual load is *tolerable*, only that it is
  the smallest measured here. Separately, the
  committed `specificity_margin` is computed oligo-wide and **overstates** true gap-level discrimination
  (§2a); a gap-centred margin and gap-centred design rule are the fix (§3b.1).
- **Predicted specificity ≠ validated specificity.** The transcriptome-wide near-match screens have been
  **run** (modelled reference junction: poor; favorable 200/8: **0 of 5 predicted clean**, designs separated
  by predicted cleavage load over >1 order of magnitude — §3a-quater) but remain
  *in-silico* — and the reference-junction BLAST number is over-called and coverage-only (§6, above). Only the
  §4 wet-lab experiment, with the controls specified there, can confirm parental and off-target sparing in
  cells.
- **No molecule, no clinical claim.** This is a computation-only, publish-to-convince draft. Nothing here
  has been tested in a patient.

---

## 7. Broader indications

⛔ **THIS SECTION IS NOT A CLAIM OF REACH; IT IS AN ACKNOWLEDGEMENT THAT THE REACH IS ALREADY DEMONSTRATED
BY OTHERS.** The junction-oligo concept is a platform, and per §1a it has **already been generalised** —
junction-directed oligonucleotides have been published against **BCR::ABL1**, **PML::RARA**,
**RUNX1::RUNX1T1**, **TMPRSS2::ERG**, **FGFR3::TACC3**, **BRD4::NUTM1**, **DNAJB1::PRKACA**,
**EWSR1::FLI1**, **PAX3::FOXO1** and **SS18::SSX1**, with parental sparing demonstrated in several and one
agent taken into clinical testing (**PMID 27166877**). ⚠ *Superseded, retained: "The junction-ASO concept
is a **platform**, not an EMC-only tactic … EMC is the proof-of-concept entry indication."* The statement is
true; presenting it as this paper's contribution was the error, and the resolved per-indication sourcing
below replaces the `[citation to verify]` that stood here.

What follows from that for **this** paper is narrower and is the honest position: EMC is not a
proof-of-concept for the platform — the platform does not need one — it is **an indication the platform has
never been applied to**, and this paper reports what happens when it is. The same design-and-screen pipeline
([`junction_aso.py`](../../modalities/junction_aso.py) plus the §3b CPU off-target screen) transfers to other
**FET-family / EWSR1-fusion sarcomas** with only the breakpoint sequence changed; what does not transfer is
the EMC-specific degrader-versus-ASO argument (§1a), which exists only because NR4A3's LBD is retained
intact in the fusion.

---

## 8. Planned high-value GPU experiment (to-do) — physics-based RNase-H1 cleavage-discrimination

Every off-target call in this paper rested on **one heuristic**: *any mismatch inside the 6-nt DNA gap
abolishes RNase-H1 cleavage.* ⛔ **That heuristic is now retired** (§3a-quater; Appendix A, entry 68): the
retrieved literature reports ~5-fold discrimination for an unmodified ASO (**PMID 23963702**) and none at all
at 16-mer length (**PMID 7567450**), so the panel is scored as a graded cleavage load and **no design is
called clean**. The red-team (F6) flagged this as the single load-bearing assumption behind the specificity
claims and was right. What the GPU experiment below would supply is the quantity the two literature bounds
disagree about — a per-mismatch, per-position discrimination factor for *this* gapmer chemistry — replacing a
two-paper prior spanning 1× to 5× with a computed one. It is
also the one place where this paper's evidence tier is **below** the companion degrader program: the ASO
work is entirely sequence/bioinformatics-level, whereas the degrader carries a physics tier (MD /
metadynamics / planned FEP). The following GPU experiment would close that gap and retire the heuristic.

**Experiment.** Estimate, from biophysics rather than a binary rule, how much a single **gap-internal
mismatch** actually disfavours RNase-H1 cleavage — i.e. the true fusion-vs-off-target discrimination margin.

- **System.** Human RNase-H1 catalytic domain in complex with a DNA:RNA heteroduplex (experimental
  structures exist, e.g. PDB 2QK9 and related human RNase-H1·hybrid structures), built with (a) the
  fully-matched gapmer:fusion-mRNA duplex (on-target) and (b) the same duplex bearing a single mismatch at
  each gap position against a representative off-target (the ≤2-mismatch hits the BLAST screen flags, e.g. at
  E12::N3). One system per gap position × mismatch identity for the shortlisted clean/near-clean designs.
- **Readout.** Two complementary estimates: (i) a **catalytic-geometry** metric — MD stability of the
  scissile-phosphate / two-metal-ion active-site geometry (Mg²⁺ coordination, in-line attack distance/angle)
  in matched vs mismatched duplexes, since a mismatch that distorts the active site is non-cleaving; and
  (ii) a **relative free-energy** estimate of duplex/complex destabilisation from the gap mismatch
  (alchemical/FEP or, cheaper, an MM-GBSA/ΔΔG screen first). Together these convert "gap mismatch ⇒ 0/1
  cleavage" into a **graded, defensible discrimination margin** per design.
- **What it changes.** Replaces the §3a-quater/§3a-quinquies binary "clean" calls with a physics-based
  cleavage-discrimination score; either firms up the predicted-clean gapmers (E7::N3 `TACGGACAATCTGCTG`,
  the 200/8 pair) or honestly downgrades them. Raises the ASO paper to the degrader's rigor tier on its
  one weak axis.
- **Cost/feasibility & sequencing (per the 2026-07-01 operating regime + trimcrae GPU rules).** Small,
  well-bounded systems (a protein domain + short duplex); far cheaper than the degrader's ternary/FEP.
  **Validate-on-one-shard first:** shake out the build + MD env on a *single* matched on-target system
  (smoke → 1 real system) before fanning out the per-position mismatch panel. Checkpoint per-window with
  `s3_upload_mode="Continuous"` (a timeout must not lose completed windows). Serialize against any other
  on-demand `ml.g5` Processing job (single-concurrency quota); the FEP tier can use the separate spot
  Training quota. **This is a to-do, not a gate on posting the preprint** — the paper is publishable now as
  a design+specificity feasibility study that names this heuristic honestly; the run *upgrades* the
  specificity claim, it is not a prerequisite for it.
- **Watched capability that would cheapen/replace it.** A calibrated **ASO off-target / RNase-H
  cleavage-activity predictor** (method-watch row) would retire the heuristic *without* this GPU run — so
  this experiment and that method-watch trigger are two routes to the same end; do whichever lands first.

**Note on scope.** This firms up **specificity**. It does **not** touch the route's dominant gate,
**delivery** (§3c) — which no in-silico experiment can currently address (see §9 method-watch: the two
delivery rows). Sequencing the GPU spend here is worthwhile *because* specificity is in-silico-tractable;
delivery is not, so it is watched, not computed.

---

## 9. Keeping this paper current — method-watch

This route's progress is **method-gated**: specific next steps unlock the moment an enabling technology
becomes usable. Those gates are watched automatically by the repo's **method-watch** (monthly cron +
on-demand: [`scripts/method-watch.mjs`](../../../scripts/method-watch.mjs),
[`.github/workflows/method-watch.yml`](../../../.github/workflows/method-watch.yml); digest published to the
`method-watch-cache` branch). The capability → action trigger table lives in
[`research/method-watch.md`](../../method-watch.md); the rows specific to this paper are:

- **ASO off-target / RNase-H cleavage-activity predictor** → retire the conservative "gap-mismatch ⇒
  non-cleaving" heuristic (§3a-quater) and re-grade predicted specificity with a calibrated model.
- **ASO/siRNA potency + target-site-accessibility predictor** → re-rank the junction designs for potency
  and replace the local-fold accessibility proxy (§3a-bis iii).
- **New patient-derived EMC / FET-fusion-sarcoma model** (cell line / organoid / PDX) → unblocks the
  decisive knockdown + parental-sparing experiment (§4) and a fusion-dependence readout.
- **In-silico oligo/nanoparticle tumour-delivery predictor** → score a targeted junction-siRNA/AOC and
  re-grade the route's dominant gate, delivery (§3c).

A digest "🆕" that crosses one of these is a prompt to update the cited section here, not an automatic edit.

---

## References

> **⭐ RETRIEVAL STATUS (2026-08-08).** Every identifier below was **returned by a Europe PMC search run on
> a GitHub runner on 2026-08-08** and is quoted from that returned record; none was written from
> recollection. The machine record — the six queries, their run IDs, the verbatim abstracts and the
> known-positive control that makes a green run mean an actual retrieval — is
> [`lit-targets-aso-verify.json`](./lit-targets-aso-verify.json), which is also the artifact
> [`lint_citations.py`](../lint_citations.py) anchors this prose against. The assessment of what the
> retrieval **changes** — including the two items where the sources argue *against* this manuscript — is
> [`aso-citations-priorart-2026-08-08.md`](./aso-citations-priorart-2026-08-08.md).
> ⚠ **Journal names are deliberately absent from entries added in that pass.** The fetch path stores Europe
> PMC's `journalTitle`, which was null for nearly every record, so no journal name would be a retrieved
> fact — and typing one from memory is the exact failure `lint_citations.py` exists for. The citation key
> is the PMID/PMCID/DOI, which a reader can check.

### Reference pool — now carrying retrieved identifiers

- **Labelle Y, Zucman J, Stenman G, Kindblom LG, Knight J, Turc-Carel C, Dockhorn-Dworniczak B, Mandahl N,
  Desmaze C, Peter M.** *Oncogenic conversion of a novel orphan nuclear receptor by chromosome
  translocation.* 1995. **PMID: 8634690 · doi:10.1093/hmg/4.12.2219**. The EMC-defining EWS::TEC(NR4A3)
  fusion; *"three different junction types"*, each joining the EWS transactivation domain to *"the entire
  TEC protein"*.
  ⚠ *Superseded, retained:* this slot previously read **"Sjögren H, et al. *EWSR1/NR4A3 fusion in
  extraskeletal myxoid chondrosarcoma.* (EMC defining fusion.)"** — a **mis-attribution**, found only once
  the entry was given an identifier. The discovery paper is Labelle et al.; Sjögren's EMC papers report the
  *variant* 5′ partners (next entry). Both groups are Stenman's, which is the likely origin of the merge.
- **Sjögren H, et al.** — the variant-partner series: **PMID: 10537274** (TAF2N/TAF15 exon 6 → *"the entire
  coding region of TEC"*, 1999) · **PMID: 11156374** (TCF12 → *"the entire TEC protein"*, 2000) ·
  **PMID: 12598313 · PMC1868116 · doi:10.1016/s0002-9440(10)63875-8** (EWS-TEC 5, TAF2N-TEC 4, TCF12-TEC 1
  across 10 EMCs, 2003).
- **Panagopoulos I, Mertens F, Isaksson M, Domanski HA, Brosjö O, Heim S, Bjerkehagen B, Sciot R, Dal Cin P,
  Fletcher JA, Fletcher CD, Mandahl N.** *Molecular genetic characterization of the EWS/CHN and RBP56/CHN
  fusion genes in extraskeletal myxoid chondrosarcoma.* 2002. **PMID: 12378528 · doi:10.1002/gcc.10127**.
  Fusion variants and partners **and** the recurrent-junction rank order (see below).
- **Crooke ST, Baker BF, Crooke RM, Liang XH.** *Antisense technology: an overview and prospectus.* **Nat Rev
  Drug Discov** 2021. **PMID: 33762737 · doi:10.1038/s41573-021-00162-z**. (Antisense / gapmer / RNase-H1
  mechanism overview.)
- **Bangerter JL, Harnisch KJ, Chen Y, Hagedorn C, Planas-Paz L, Pauli C.** *Establishment, characterization
  and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma (EMC) cell models.* 2023.
  **PMID: 36316541 · PMC9813045 · doi:10.1007/s13577-022-00818-x**. USZ20-EMC1 (EWSR1-NR4A3) and USZ22-EMC2
  (TAF15-NR4A3).
- **Iwata S, Noguchi R, Osaki J, Adachi Y, Shiota Y, Osaki S, Nishino S, Yoshida A, Ohtori S, Kawai A,
  Kondo T.** *Establishment and characterization of NCC-EMC1-C1: a novel patient-derived cell line of
  extraskeletal myxoid chondrosarcoma.* 2025. **PMID: 40580361 · doi:10.1007/s13577-025-01250-7**.
  ⚠ **Not open access — PAYWALLED.** Only the abstract could be retrieved.
- **Mullican SE, et al.** *Abrogation of nuclear receptors Nr4a3 and Nr4a1 leads to development of acute
  myeloid leukemia.* **Nat Med** 2007. **PMID: 17515897 · doi:10.1038/nm1579**. (Wild-type NR4A1/NR4A3 loss
  → AML — the tumour-suppressor liability the junction ASO avoids.) *Superseded, retained:* this entry
  previously carried an abbreviated title.
- **Safe S, Karki K.** *The Paradoxical Roles of Orphan Nuclear Receptor 4A (NR4A) in Cancer.* **Mol Cancer
  Res** 2021. **PMID: 33106376 · PMC7864866 · doi:10.1158/1541-7786.mcr-20-0707**.
- **Le Guilloux V, Schmidtke P, Tufféry P.** *Fpocket: an open source platform for ligand pocket detection.*
  **BMC Bioinformatics** 2009. **PMID: 19486540 · PMC2700099 · doi:10.1186/1471-2105-10-168**. (Companion
  structural/degrader work; **not used in this RNA-level analysis** — a reference used by nothing belongs in
  the companion paper, not here.)
- **Varadi M, et al.** *AlphaFold Protein Structure Database.* **Nucleic Acids Res** 2022.
  **PMID: 34791371 · PMC8728224 · doi:10.1093/nar/gkab1061**. (Companion structural work; **not used here** —
  same note as above.)

### Formerly "to verify" — six resolved, two closed as evidence-backed absences

- ✅ **Rank-order of recurrent EMC exon junctions — RESOLVED from the primary literature.**
  **PMID: 12378528**: across 18 EMCs, *"The most frequent EWS/CHN transcript (type 1; 10 tumors), involved
  fusion of EWS exon 12 with CHN exon 3, and the second most common (type 5; two cases) was fusion of EWS
  exon 13 with CHN exon 3. In all tumors with RBP56/CHN fusion, exon 6 of RBP56 was fused to exon 3 of
  CHN. … In CHN, 12 breakpoints were found in intron 2 and only two in intron 1. In EWS, the breaks occurred
  in introns 7 (one break), 12 (eight breaks), and 13 (one break)"* (`CHN` = `TEC` = *NR4A3*;
  `RBP56` = `TAF2N` = *TAF15*). Independent corroboration: **PMID: 11679947 ·
  doi:10.1053/hupa.2001.28226** (*"EWS-CHN type 1 in 11 cases, EWS-CHN type 2 in 1, and TAF2N-CHN in 3"*
  of 18) and **PMID: 9060841 · PMC1857890**. Further NR4A3 5′ partners: **PMID: 34124809 ·
  doi:10.1002/gcc.22976** (SMARCA2 exon 3 → NR4A3 exon 3); an EMC driven by **NR4A2** rather than NR4A3:
  **PMID: 41315062 · doi:10.1007/s00428-025-04352-7**.
  ⭐ **This is also external corroboration of the 2026-08-06 exon-index correction.** Twelve of fourteen
  genomic breaks map to *CHN* **intron 2**, and Labelle (**PMID: 8634690**) and Sjögren (**PMID: 10537274**,
  **PMID: 11156374**) all describe the product as containing the **entire** TEC/NR4A3 protein — i.e. NR4A3
  resuming at residue 1, which is the corrected
  [`fusion-object-inventory.json`](../../modalities/fusion-object-inventory.json)
  `nr4a3_resume_range_across_plausible_breakpoints` of **[1, 1]**, and is incompatible with the retracted
  panels' residue 361. ⚠ *Superseded, retained:* *"the exon rank-order now has no in-repo support at all and
  rests entirely on the unfetched primary literature."* The literature is no longer unfetched; the in-repo
  situation is unchanged and the retraction stands.
- ⛔ **Quantitative RNase-H1 tolerance of a single gap-internal mismatch — RESOLVED, AND THE SOURCES ARGUE
  AGAINST THE HEURISTIC §3a-quater USES.** **PMID: 23963702 · PMC3834808 · doi:10.1093/nar/gkt725**
  (Østergaard et al.): *"ASOs have been previously shown to discriminate single nucleotide changes in
  targeted RNAs with ∼5-fold selectivity. Based on RNase H enzymology, we enhanced single nucleotide
  discrimination by positional incorporation of chemical modifications within the oligonucleotide to limit
  RNase H cleavage of the non-targeted transcript. The resulting oligonucleotides demonstrate >100-fold
  discrimination for a single nucleotide change at an SNP site…"* — so a single mismatch in the catalytic
  window of an **unmodified** gapmer reduces cleavage roughly **five-fold rather than abolishing it**, and
  the >100-fold figure requires chemistry this manuscript's designs do not carry. Concordant:
  **PMID: 28624195 · PMC5363678 · doi:10.1016/j.omtn.2017.02.001** (*"Certain mismatches, however, allow
  ASOs to bind at physiological conditions and result in RNA cleavage mediated by RNase H"*);
  **PMID: 28970564 · PMC5624880 · doi:10.1038/s41598-017-12844-z** (of *"over 120 gapmers tested"*, three
  gave preferential mutant cleavage in cells); **PMID: 38993932 · PMC11238192 ·
  doi:10.1016/j.omtn.2024.102237** (*"Initial gapmer ASO design exhibited high efficiency but poor
  specificity for the mutant allele"*); **PMID: 42327837 · PMC13276142 · doi:10.1016/j.omtn.2026.102937**
  (a 2′-OMe placed at gap position 2 *"to … restrict RNase H1 cleavage"* — engineered, not intrinsic);
  **PMID: 7731809 · PMC306791 · doi:10.1093/nar/23.6.954**; **PMID: 26544037 · PMC4704561 ·
  doi:10.1371/journal.pone.0142139**; **PMID: 32092825 · PMC7033438 · doi:10.1016/j.omtn.2020.01.012**;
  **PMID: 35085461 · doi:10.1089/nat.2021.0009**. Measured gapmer off-target behaviour:
  **PMID: 29790953 · doi:10.1093/nar/gky397**, **PMID: 31637814 · doi:10.1111/gtc.12730**,
  **PMID: 36276652 · doi:10.7150/thno.77830**.
  ⚠ **Directly relevant to this manuscript's 16-mer geometry: PMID: 7567450 · PMC307218 ·
  doi:10.1093/nar/23.17.3411** — *"Short oligonucleotides (12- or 13mers) centered on the mutation had a very
  high discriminatory efficiency. Longer oligonucleotides (16mers) did not discriminate efficiently between
  the mutated and the normal mRNA."*
  ⛔ **Therefore §3a-quater's "2 of 5 predicted off-target-clean" is a RANKING, not a clean/dirty call**, and
  the sentence there calling "gap mismatch ⇒ no cleavage" *conservative* no longer holds: against a ~5-fold
  figure it is optimistic. No retrieved source reports a tolerance number for a 6-nt DNA gap between 5-nt LNA
  wings specifically, so the ~5-fold value must be cited as the field's general figure.
  ✅ **RE-SCORING APPLIED 2026-08-08.** Both identifiers were re-verified against PubMed `esummary`,
  Europe PMC `resultType=core` and Crossref in one CI run (31276141296) — title and byline agree on all
  three registries for both — and the panel was regraded by
  [`junction_aso_offtarget.grade_panel`](../../modalities/junction_aso_offtarget.py) into
  [`junction-aso-offtarget-bp200-8-gapres-graded.json`](../../modalities/junction-aso-offtarget-bp200-8-gapres-graded.json).
  **The new figure is 0 of 5 under both bounds** (§3a-quater; Appendix A, entry 68). The same regrade was run
  on the real-junction panels
  ([`-e7n3-graded.json`](../../modalities/junction-aso-offtarget-e7n3-graded.json),
  [`-e12n3-graded.json`](../../modalities/junction-aso-offtarget-e12n3-graded.json)) and changes no headline
  there, because those panels already read 0 clean under the retired assumption.
- ✅ **Non-EWSR1/FET recurrent-fusion cancers as platform extensions — RESOLVED, and they are prior art
  rather than prospects.** See the prior-art subsection below.
- ◐ **Whether the EMC-line papers report an immunophenotype / surface-marker IHC and/or deposited RNA-seq —
  ANSWERED for one, PAYWALLED for the other.** **PMID: 36316541** is open access and was retrieved in full:
  *"The cells were molecularly characterized using DNA sequencing and methylation profiling."* Its full text
  contains **no** immunohistochemistry, **no** RNA-seq and **no** GEO/SRA accession — so the §3c "decisive
  upgrade" is not merely on request for this paper, it is not in it. **PMID: 40580361** is **paywalled**;
  its abstract reports a 221-agent drug screen and carries no immunophenotype and no accession, and the item
  stays open **for that paper by name**.
- ⛔ **B7-H3 (CD276) surface expression in EMC specifically — CLOSED AS AN EVIDENCE-BACKED ABSENCE.** A
  754-record EMC corpus whose query **named** `B7-H3` and `CD276` returned **zero** EMC records mentioning
  either in title or abstract, and a full-text grep across its 449 open-access bodies found no EMC-specific
  B7-H3 result. Quote the query, never the bare zero — the query is in
  [`lit-targets-aso-verify.json`](./lit-targets-aso-verify.json). This is concordant with §3c, which already
  calls the B7-H3 nomination an extrapolation from other sarcomas.
- ⛔ **EMC-specific surface expression of the surfaceome-scan shortlist (CDH11, FGFR1, GPC2, PTK7,
  MCAM/CD146), and an EMC-enriched receptor for AOC / targeted-nanoparticle delivery — NOT A MISSING
  CITATION, A MISSING STUDY.** The same query named CDH11, GPC2, PTK7, MCAM and CD146; no EMC record reports
  surface expression of any of them in EMC. There is no citation to supply, and the shortlist stays
  surrogate-derived exactly as §3c states.

### Prior art — junction-directed oligonucleotides against fusion oncogenes (retrieved 2026-08-08)

✅ **§1a IS THAT RELATED-WORK SECTION, added 2026-08-08.** It is built only from what this subsection and
[`lit-targets-aso-verify.json`](lit-targets-aso-verify.json) establish, it concedes in its first sentence
that the method-level novelty is nil, and it states what remains as an **indication-level** claim.
⚠ *Superseded, retained: "This manuscript has no related-work section, and the modality it proposes has a
35-year, continuous, clinically-tested precedent."* The second clause is unchanged and true; only the
first is out of date. The full assessment — including which of this paper's claims survive it — is
[`aso-citations-priorart-2026-08-08.md`](./aso-citations-priorart-2026-08-08.md). Two corpora totalling
5,385 records were searched; the sources are listed here so the manuscript cites the precedent rather than
being shown it.

- **The rationale, already stated as a general principle.** **PMID: 16083345 ·
  doi:10.1517/14728222.9.4.825** (Maksimenko & Malvy, 2005): *"the junction point at the mRNA level offers a
  target for short therapeutic nucleic acids that is present only in the cancer cells and not in the normal
  tissues of a patient. Several teams have, therefore, investigated the activity of antisense
  oligonucleotides and siRNAs targeted against the junction point."*
- **Antisense at a fusion breakpoint, RNase-H-dependent, in a sarcoma.** **PMID: 9049825 ·
  doi:10.1023/a:1005716926800** (Toretsky et al., 1997): *"a series of antisense ODN directed toward the
  breakpoint region … Exogenously added RNase H was found to be required for translation inhibition."*
  Earlier and adjacent: **PMID: 1794439** (BCR/ABL breakpoint ODN with a scrambled control sparing normal
  marrow, 1991), **PMID: 7566963** (1995), **PMID: 9005992 · PMC507791 · doi:10.1172/jci119152** (1997).
- **Catalytic-nucleic-acid route, with an explicit warning about long junction arms.** **PMID: 7987829**
  (PML/RARα-discriminating ribozyme, 1994), **PMID: 8127665 · PMC523580 · doi:10.1093/nar/22.3.301**,
  **PMID: 9150886**, **PMID: 9224607 · PMC146844 · doi:10.1093/nar/25.15.3074** (*"Several hammerhead
  ribozymes with relatively long junction-recognition sequences have poor substrate-specificity"*).
- **Junction-restricted design methodology already exists.** **PMID: 26627251 · PMC4672813 ·
  doi:10.1073/pnas.1517039112** (*"in some cases (e.g., a fusion junction site) region choice is restricted.
  In these instances, alternative approaches are necessary"*) and **PMID: 31728968 ·
  doi:10.1007/978-1-4939-9904-0_11** (*"sequence homology restricts the targeting region to the chimeric
  junction and can result in off-target effects on the parental genes"*, with design guidelines and the
  controls §4 proposes).
- **Parental sparing demonstrated at a bench, repeatedly.** **PMID: 33241214 · PMC7680176 ·
  doi:10.1093/noajnl/vdaa132** (FGFR3-TACC3 breakpoint siRNAs *"did not affect levels of wild-type (WT)
  FGFR3 or TACC3"*); **PMID: 36265509 · PMC10101799 · doi:10.4143/crt.2022.910** (BRD4-NUTM1 junction siRNA
  *"without affecting the endogenous expression of the parent genes"*); **PMID: 36302174 · PMC9811160 ·
  doi:10.1158/1078-0432.ccr-22-1851** (shRNAs *"tiled over the fusion junction"* of DNAJB1-PRKACA);
  **PMID: 23052253 · PMC3525716** and **PMID: 31614005 · PMC6925833** (TMPRSS2/ERG);
  **PMID: 21846246 · PMC3237690** (PML-RARα); **PMID: 31104089 · PMC7116733** and **PMID: 40991849 ·
  PMC12824707 · doi:10.1182/blood.2025028988** (BCR-ABL, RUNX1::RUNX1T1).
- **Sarcoma fusions specifically.** **PMID: 20648560 · doi:10.1002/ijc.25564** (siRNA *"targeting the
  breakpoint of EWS/Fli-1"*); **PMID: 27261335 · doi:10.1016/j.jconrel.2016.05.063** (siRNA *"directed
  against the breakpoint of P3F"* — PAX3-FOXO1 — in RGD-targeted nanoparticles);
  **PMID: 20198325 · doi:10.3892/ijo_00000559** and **PMID: 23716114 · PMC3916608** (SS18-SSX1, synovial
  sarcoma); **PMID: 14620508 · doi:10.1023/a:1026122914852** (*"Oligonucleotides targeted against a junction
  oncogene are made efficient by nanotechnologies"*).
- **The closest program-level precedent, and the one that bears on §3c.** **PMID: 37980543 · PMC10787139 ·
  doi:10.1016/j.ymthe.2023.11.012** — a GalNAc-conjugated siRNA against the DNAJB1::PRKACA **fusion
  junction** in fibrolamellar hepatocellular carcinoma, i.e. a rare fusion-driven cancer in which the
  targeting arm was supplied by a receptor conjugate. ⚠ ASGPR/GalNAc is hepatocyte-directed and is **not**
  available to a soft-tissue sarcoma, so this bears on §3c as evidence that the delivery gate is passable in
  principle, **not** as a route for EMC.
- **Preclinical stage.** **PMID: 27166877 · PMC5023384 · doi:10.1038/mt.2016.93** — bi-shRNA EWS/FLI1
  lipoplex, which *"targets the identical type 1 translocation junction region of the EWS/FLI1
  transcribed mRNA"*, taken through IND-enabling work and arguing for clinical testing. Review, 2026:
  **PMID: 42110475 · PMC13156592 · doi:10.1016/j.omton.2026.201213**.
  ⚠ *Superseded, retained: "**Clinical stage** … follow-through in patients at PMID: 36780200"
  (corrected 2026-08-12). PMID 36780200 is Vigil, a bi-shRNA against* furin*, not against EWS/FLI1
  — see §1a(v).*
- **What the search did NOT find, with the accounting that makes it auditable.** No junction-directed
  oligonucleotide against **EWSR1::NR4A3**, or against any NR4A3 fusion. Across the two corpora — 5,385 rows,
  **5,153 unique records** — EWSR1::NR4A3 is named in **4 rows (3 distinct papers) and none carries an
  oligonucleotide modality** (**PMID: 40762284**, **PMID: 29937513**, **PMID: 25097177**), against **108**
  records combining an oligonucleotide modality with a junction/breakpoint term for BCR::ABL1, **37** for
  EWSR1::FLI1, **8** for RUNX1::RUNX1T1 and **4** for PAX3::FOXO1. Per-fusion table:
  [`lit-targets-aso-verify.json`](./lit-targets-aso-verify.json) → `prior_art_accounting`. ⚠ The method is
  title/abstract-only, so every count is a **lower** bound — the right direction here, since a lower-bound
  method cannot manufacture a zero it did not observe. Also not found: no **gapmer** — as distinct from siRNA/shRNA/ribozyme/unmodified
  ODN — directed at any fusion junction in a modern LNA/cEt architecture. ⚠ Read the second of those
  together with the RNase-H1 item above before treating it as an opportunity: a gapmer's single-base
  discrimination is poor without engineered gap chemistry, which is a plausible reason the field went to
  RNAi for junctions.

**Reproducibility.** The real results cited here are committed CPU outputs (snapshotted on the main branch;
refreshed by GitHub Actions on the `modalities-cache` branch):

- [`junction-aso-designs.json`](../../modalities/junction-aso-designs.json) — 5 junction-spanning 5-6-5 gapmer
  designs, from [`junction_aso.py`](../../modalities/junction_aso.py).
- [`junction-aso-offtarget.json`](../../modalities/junction-aso-offtarget.json) — NCBI BLAST API (blastn-short
  vs RefSeq RNA) gap-spanning off-target screen of the canonical designs, from
  [`junction_aso_offtarget.py`](../../modalities/junction_aso_offtarget.py) (HITLIST-capped at 50; over-calls).
- [`aso-insilico-evaluation.json`](../../modalities/aso-insilico-evaluation.json) — **uncapped** full-RefSeq
  (186,185-transcript) off-target screen + ViennaRNA accessibility + siRNA-seed module of the canonical
  designs, from [`aso_insilico.py`](../../modalities/aso_insilico.py).
- [`junction-sirna-designs.json`](../../modalities/junction-sirna-designs.json) — junction siRNA route, from
  [`junction_sirna.py`](../../modalities/junction_sirna.py).
- [`junction-breakpoint-scan.json`](../../modalities/junction-breakpoint-scan.json) — 390-breakpoint GC/
  complexity/parent-specificity triage sweep, from
  [`junction_breakpoint_scan.py`](../../modalities/junction_breakpoint_scan.py).
- [`junction-aso-offtarget-bp200-8.json`](../../modalities/junction-aso-offtarget-bp200-8.json) and its
  gap-mismatch-resolved companion
  [`junction-aso-offtarget-bp200-8-gapres.json`](../../modalities/junction-aso-offtarget-bp200-8-gapres.json) —
  the BLAST off-target screen re-run on the favorable EWSR1-keep-200 / NR4A3-from-8 breakpoint, resolved to
  true RNase-H cleavage risk, from [`junction_aso_offtarget.py`](../../modalities/junction_aso_offtarget.py).
- [`aso-insilico-evaluation-bp200-8.json`](../../modalities/aso-insilico-evaluation-bp200-8.json) — the
  **uncapped** full-RefSeq off-target + accessibility + siRNA-seed evaluation re-run on the same favorable
  breakpoint (4 of 5 gapmers with zero ≤1-mismatch off-targets), from
  [`aso_insilico.py`](../../modalities/aso_insilico.py) (breakpoint-parameterised via env).
- ⛔ **Real clinical junctions — RETRACTED, AND THREE FIFTHS OF IT NEVER EXISTED (§3a-quinquies).**
  *Superseded, retained:* `junction-aso-designs-{e7n3,e9n3,e10n3,e12n3,e13n3}.json`,
  `junction-aso-offtarget-{e7n3,e9n3,e10n3,e12n3,e13n3}.json`,
  `aso-insilico-evaluation-{e7n3,e9n3,e10n3,e12n3,e13n3}.json`,
  `junction-sirna-designs-{e7n3,e9n3,e10n3,e12n3,e13n3}.json`, *and the claims attached to them (3/5
  siRNA guides passing at E10::N3 and E12::N3 at min GC 42.1%, 0/5 at E7/E9/E13, and the gapmer↔siRNA
  complementarity conclusion).*
  **Measured 2026-08-06 — what is actually on disk:** exactly six files,
  `junction-aso-designs-e{7,12}n3.json`, `junction-aso-offtarget-e{7,12}n3.json` and
  `aso-insilico-evaluation-e{7,12}n3.json`, **all six carrying a `_RETRACTED_SEAM` banner.** The
  `e9n3`, `e10n3` and `e13n3` variants and **every** exon-mode siRNA file are absent from
  `origin/main`, from `origin/modalities-cache` and from every commit reachable in this clone.
  ⚠ **THE `origin/modalities-cache` HALF OF THAT SENTENCE IS FALSE — MEASURED 2026-08-08.**
  `git cat-file -e origin/modalities-cache:<path>` finds **13 of those 14 files present at the tip of
  `origin/modalities-cache`**; only `junction-aso-designs-e9n3.json` is genuinely absent everywhere.
  Thirteen were added in one commit — `30eb56842`, 2026-07-03, `github-actions[bot]`, *"ASO
  real/reference junction screens: design + gap-resolved BLAST + uncapped eval + siRNA"*, 13 files,
  3,400 insertions — reachable from `origin/modalities-cache` and from no other ref. The `origin/main`
  half of the sentence is correct; this is the branch-drift failure of CLAUDE.md §7, where an artifact
  whose only home is a non-default branch reads as non-existent from `main`.
  **What this does and does not change.** It removes the *second, independent* ground for withdrawal
  ("unverifiable") — those files are verifiable. It changes **nothing** about the seam defect, which
  retracts the claims on its own and is unaffected. ⛔ **And it exposes a worse state than the one it
  corrects:** those 13 cache-branch files carry the retracted seam **with no banner** — e.g.
  `junction-sirna-designs-e12n3.json` there still reads `"junction_context_mRNA":
  "AATGGTTTGATG|TTGTCCGTACAG"` with `"assumption": false` and `"n_passing_all_filters": 3`. The
  `e7n3`/`e12n3` files on `main` were regenerated at the corrected seam on 2026-08-06; their
  cache-branch siblings were not. Reported, not fixed — that branch is written by a workflow. Full
  measurement: [`aso-citations-priorart-2026-08-08.md`](./aso-citations-priorart-2026-08-08.md) Part 3.
  ✅ **Those six were REGENERATED at the corrected seam on 2026-08-06 and no longer carry the banner
  (§3a-sexies).** ⚠ *Superseded, retained: "all six carrying a `_RETRACTED_SEAM` banner."* The count
  of files at the CORRECTED seam is unchanged — **six files, two junctions**.
  ⛔ **CORRECTED 2026-08-08.** ⚠ *Superseded, retained: "the `e9n3`/`e10n3`/`e13n3` and siRNA
  variants are still absent … A citation to a file that does not exist cannot be checked by a
  reader and must not appear in a manuscript; these are withdrawn as unverifiable."* **They are not
  absent.** Thirteen of them sit at the tip of `origin/modalities-cache`, added 2026-07-03 by commit
  `30eb5684` and unmodified since; only `junction-aso-designs-e9n3.json` is genuinely missing. The
  2026-08-06 search ran in a clone that had not fetched the branch. The withdrawal below stands and
  is strengthened: those thirteen carry the **retracted acceptor seam** `TTGTCCGTACAG` against the
  corrected `ATATGCCCTGCG`, so they are withdrawn as measurably wrong rather than as unreadable, and
  each now carries a `⛔_RETRACTED_SEAMS` banner in the file itself
  ([`junction_seam_retraction.py`](../../modalities/junction_seam_retraction.py)). The e11:3 no-output is root-caused in
  §3a-quinquies and is not an exon-boundary uncertainty.
  ⚠ *One thing here was never in doubt and is not withdrawn:* the `gap_specificity_margin`
  gap-level discriminator (§2a/§3b.1) is a property of `junction_aso.design()` and is independent of
  which seam it is given.
- **EMC surfaceome scan (§3c):** [`emc-surfaceome-scan.json`](../../modalities/emc-surfaceome-scan.json) (+ `.png`)
  from [`emc_surfaceome_scan.py`](../../modalities/emc_surfaceome_scan.py) — unbiased UniProt surfaceome (2,820
  genes) ranked by expression across the EMC-surrogate translocation-sarcoma DepMap class; names a data-ranked
  delivery/CAR/ADC targeting-antigen shortlist (surrogate, not EMC; myxoid n=1; rest≠normal tissue).

No GPU computation was performed for this draft (the RNase-H1 cleavage-discrimination MD of §8 is the one
planned GPU experiment; all results above are CPU, via GitHub Actions → `modalities-cache`).


---

## Appendix A — retraction and correction record (2026-08-06)

*Moved here from the head of the manuscript. Retained verbatim: rule 1.2 of this repository's
maintenance contract requires that a superseded number is registered rather than dropped, and an
appendix is where that bookkeeping belongs — not in the running text, where the old values read as
current.*

> # ⛔⛔ RETRACTION — THE REAL-EXON HALF OF THIS MANUSCRIPT (2026-08-06)
>
> **NOT SUBMITTABLE IN ITS CURRENT STATE. Every design, GC value, off-target count, seam and
> headline gapmer attributed below to a "real" EWSR1 exon-*n* :: NR4A3 exon-3 junction is
> RETRACTED and must not be quoted.** The codon-space modelled half of the paper (§3a, §3a-bis,
> §3a-ter, §3a-quater, the 390-breakpoint scan and the 200/8 screens) is **untouched by this** —
> it never used the exon index. What falls is §3a-quinquies and every sentence that leans on it.
>
> **What went wrong, measured.** `junction_aso.py`'s `FUSION_JUNCTION_MODE=real` path indexed a
> table keyed by **coding** exon with a **transcript** exon number. NR4A3 `ENST00000395097` has 8
> transcript exons of which 1 and 2 carry no coding sequence, so the label "NR4A3 exon 3"
> addressed the third *coding* exon. The committed seam `TTGTCCGTACAG` sits at **NR4A3 CDS nt
> 1081**, i.e. NR4A3 resuming at **residue 361** — bit-for-bit the value
> [`fusion-neoantigen-retraction.json`](../../modalities/fusion-neoantigen-retraction.json) grades
> **`SEAM_NOT_PRODUCED`**, against a corrected
> `nr4a3_resume_range_across_plausible_breakpoints` of **[1, 1]** in
> [`fusion-object-inventory.json`](../../modalities/fusion-object-inventory.json). So those panels
> describe a chimera missing NR4A3 residues 1–360 — AF1 and the first zinc finger of the C4 DBD,
> which opens at C292 — that no plausible breakpoint in the declared windows produces.
> Primary record: [`systems/AUDIT-2026-08-06-routes.md`](../../../systems/AUDIT-2026-08-06-routes.md)
> finding **X14**.
>
> **⚠ Why this manuscript could not catch it, and it is the transferable lesson.** The **EWSR1
> side reproduced correctly throughout** (EWSR1 transcript exon 1 *is* coding, so rank equals
> coding index there). The E7::N3 and E12::N3 panels therefore agreed with each other, and §3a-quinquies
> read that agreement as corroboration — *"Both share the NR4A3 exon-3 right-side seam … **as
> expected**."* **Two artifacts agreeing is not evidence when one defect produces both.**
>
> **⭐ A second reading, taken 2026-08-06, that the paper had already recorded without knowing it.**
> §3a-quinquies flags E11::N3 as an unexplained no-output and offers *"most likely … our exon
> indexing for EWSR1 exon 11 → NR4A3 exon 3 may not be in-frame as joined."* That guess was wrong
> and the real cause is arithmetic. Under the defective index the chimeric CDS is in frame exactly
> when the EWSR1 cut offset ≡ 1081 ≡ 1 (mod 3). Read off the committed exon audit
> ([`nr4a3-exon-audit.json`](../../modalities/nr4a3-exon-audit.json)): e7 793, e9 1012, e10 1045,
> e12 1294, e13 1417 are all ≡ 1 — and **e11 1164 ≡ 0**. The set of junctions the pipeline emitted
> ({7, 9, 10, 12, 13}) and the single one it refused ({11}) are **exactly** what the off-by-two
> predicts. The "integrity flag" was the defect announcing itself, and it was read as an exon-boundary
> uncertainty for a month.
>
> **⛔ Three panels this manuscript cites have never existed.** §3a-quinquies claims a "full
> recurrent-junction panel (now run, real, committed — 2026-07-03)" over
> `junction-aso-offtarget-e{9,10,13}n3.json` and `junction-sirna-designs-e{7,9,10,12,13}n3.json`.
> ⛔ **CORRECTED 2026-08-08 — THIS SEARCH WAS WRONG, AND THE FILES EXIST.** ⚠ *Superseded,
> retained:* "Searched 2026-08-06: **none of those filenames is present on `origin/main`, on
> `origin/modalities-cache`, or in any commit reachable from this clone's refs.** Only the E7::N3
> and E12::N3 files exist, and those six are the ones carrying `_RETRACTED_SEAM` banners."
> **Measured 2026-08-08 at the tip of `origin/modalities-cache`: THIRTEEN of them are there** —
> `junction-aso-designs-e{10,13}n3.json`, `junction-aso-offtarget-e{9,10,13}n3.json`,
> `aso-insilico-evaluation-e{9,10,13}n3.json` and `junction-sirna-designs-e{7,9,10,12,13}n3.json` —
> added by commit `30eb5684` on **2026-07-03**, the single CI commit from `aso-offtarget.yml` that
> created all thirteen, and unmodified since. Only `junction-aso-designs-e9n3.json` is genuinely
> absent. **The 2026-08-06 search was run in a clone that had not fetched the branch**, so it
> reported an unfetched ref as an empty one: an absent reading read as a reading of absence, in the
> one place where it became a published claim about what a reader can check.
> **What does NOT change is the withdrawal.** Every quantitative statement sourced to E9/E10/E13 —
> the siRNA GC ranges, "a fully-clean 16-mer gapmer appears at 1 of 5 junctions", and the
> gapmer+siRNA panel-coverage conclusion — stays withdrawn, and now on the STRONGER of the two
> grounds rather than the weaker: those files do not merely fail to be readable, they are readable
> and **carry the retracted acceptor seam `TTGTCCGTACAG`** (NR4A3 CDS nt 1081, residue 361) against
> the corrected `ATATGCCCTGCG`. All thirteen were graded and bannered
> `⛔_RETRACTED_SEAMS` by [`junction_seam_retraction.py`](../../modalities/junction_seam_retraction.py),
> whose sweep now runs inside `aso-offtarget.yml`'s publish step so the branch's owner cannot
> republish an unbannered one.
>
> **What is owed, and its state.** ⚠ *Superseded, retained (the state as of the morning of
> 2026-08-06):* `junction_aso.py` was corrected (twice — see the two-defect block
> in that module) and the corrected real-exon mode is built and unit-tested. Regeneration needs a
> live Ensembl read, which the dev sandbox's egress proxy refuses (measured 2026-08-06:
> `CONNECT tunnel failed, response 403` to `rest.ensembl.org`), so it must run in CI —
> `emc-expression-datasets.yml` `mode: aso-junction`. **Until that run lands, the corrected seam,
> the corrected GC values and the corrected off-target load are UNKNOWN.** They are not "expected
> to be similar"; the entire NR4A3 half of every oligo changes, and every oligo in this panel
> spans the seam by construction, so **not one design survives**.
>
> # ✅ REGENERATED, AND THE RETRACTION IS LIFTED FOR THE TWO PANELS THAT EXIST (2026-08-06, later the same day)
>
> **What is now measured, and what is still withdrawn — read both halves.**
>
> **(a) The seam.** The corrected junction resumes NR4A3 at **residue 1**, inside the corrected
> plausible range **[1, 1]**. The corrected mRNA seams are
> **`ACGGGCAGCAGA|ATATGCCCTGCG`** (E7::N3) and **`AATGGTTTGATG|ATATGCCCTGCG`** (E12::N3), against
> the retracted `…|TTGTCCGTACAG` both panels shared.
>
> **(b) The thing the earlier block could not state, because it needed one number nobody had
> measured.** A fusion transcript retains the acceptor exon WHOLE, 5′UTR included, so the register
> is set by the donor cut *and* by however many NR4A3 exon-3 bases sit 5′ of NR4A3's own ATG — call
> it *U*. `junction_aso.py`'s two-defect block records *U* as unknown from any artifact in this
> repo. That was true of [`nr4a3-exon-audit.json`](../../modalities/nr4a3-exon-audit.json), which
> records coding nt per exon only, and **false of the repo**:
> [`emc-construct-inputs.json`](../../modalities/emc-construct-inputs.json) carries the spliced cDNA,
> per-exon lengths and `utr5_len` for both genes, fetched from the same Ensembl endpoint on
> 2026-08-03 with its own self-checks recorded. **Measured: NR4A3 transcript exons 1–2 end at cDNA
> nt 697 and the CDS starts at nt 699, so *U* = 2.** Independent cross-check inside the same
> file: exon 3 is 953 nt and the exon audit records 951 CODING nt in it, and 953 − 951 = 2.
>
> **(c) That resolves a caveat this repo had recorded as open, and it changes the answer by a
> residue.** EWSR1 exon 7 ends at coding nt 793 = 264 whole residues **+ 1 nt**, so (793 + 2) mod 3
> = 0: the chimeric ORF is in frame **and** the leftover EWSR1 nucleotide plus the two retained
> acceptor-UTR nucleotides form a codon belonging to **neither parent**. At E7::N3 that codon is
> `AAT` = **Asn**, so the protein seam is `…SQQSSSYGQQ-**N**-MPCVQAQYSP…`. One home for the
> resolution: [`fusion-object-inventory.json`](../../modalities/fusion-object-inventory.json) →
> `gate._phase_note_resolution`.
>
> **(d) And it inverts the E11::N3 arithmetic, which is the sharpest check available that the
> correction is the right one.** Under the *defective* index the chimeric CDS was in frame exactly
> when the EWSR1 cut ≡ 1 (mod 3) — admitting e7/e9/e10/e12/e13 and refusing **e11**. Under the
> corrected mRNA-level model the condition is (cut + 2) ≡ 0 (mod 3) — which admits **e7 and e12,
> the two junctions this manuscript leads with**, and now refuses **e11**. Both models refuse e11
> and for different arithmetic; the corrected one restores exactly the junctions the defective one
> was accidentally admitting. Every declared exon pair is graded in
> [`junction-mrna-frame-audit.json`](../../modalities/junction-mrna-frame-audit.json) — the table this
> lane never had, which designs nothing and refuses out loud.
>
> **(e) Two independent reads agree, and this time they can fail independently.** The BLAST screen
> ran on a GitHub-hosted CPU runner from a **live Ensembl read** (2026-08-06); the audit, the design
> panels and the artifact headers were rebuilt offline from the **2026-08-03 committed cache**. The
> two produce **byte-identical designs and an identical measured junction**. That is the check the
> retracted panels never had: E7::N3 and E12::N3 agreeing was one defect producing both, whereas
> these are two separate acquisitions of the transcript model.
>
> **(f) STILL WITHDRAWN — but for a different and stronger reason than this paragraph gave.**
> ⚠ *Superseded, retained:* "The E9/E10/E13 panels and the `junction-sirna-designs-e*n3` files **do
> not exist** and were never regenerated, because there was nothing to regenerate." **Twelve of the
> thirteen do exist**, on `origin/modalities-cache` since 2026-07-03 (only
> `junction-aso-designs-e9n3.json` is genuinely absent); the search that concluded otherwise had not
> fetched the branch — see the correction above. They were not regenerated, which is the true half
> of the sentence, and they carry the retracted acceptor seam, which is why every statement sourced
> to them — the siRNA GC ranges, *"a fully-clean 16-mer gapmer appears at 1 of 5 junctions"*, and
> the gapmer+siRNA panel-coverage conclusion — remains withdrawn. They are now withdrawn as
> **measurably wrong** rather than as unverifiable, and all thirteen carry a `⛔_RETRACTED_SEAMS`
> banner saying so in the file itself. **The corrected panel still covers 2 junctions, not 5.**
> ⚠ The three E9/E10/E13 junctions are graded **EMITTABLE** under the corrected model
> ([`junction-mrna-frame-audit.json`](../../modalities/junction-mrna-frame-audit.json)), so they COULD
> be rebuilt; until they are, nothing about them may be quoted.
>
> **(g) The corrected result does not restore the retracted headline — it refutes half of it.** See
> §3a-sexies. Chemistry improves at the real seams; predicted specificity does **not**, and the
> retracted *"a gapmer predicted clean on both screens at E7::N3"* is contradicted by the corrected
> screen. Delivery (§3c) remains the dominant gate and nothing here speaks to potency, knockdown,
> tolerability or clinical use.
>
> **What survives the retraction** — narrower than the paper's current framing and stated at full
> strength: the *rationale* (a breakpoint mRNA seam present only in the chimera) is a sequence
> argument that does not depend on which exon pair is right; the codon-space screens and the
> 390-breakpoint scan are unaffected; and `junction_breakpoint_scan.py` was never implicated,
> because it deliberately refuses the exon→CDS mapping and works in codon space. ⚠ *Superseded,
> retained: the earlier and broader claim that "the ASO lane is unaffected" by the 2026-08-03 exon
> correction. That was true of `junction_breakpoint_scan.py` and false of the lane — the earlier
> audit checked one of the lane's two modules and generalised.*
## Appendix B — the orientation-filter audit, and the numbers it superseded (2026-08-12)

*Registered here rather than in the submission text, per rule 1.2: the superseded values below must
stay quotable as history and must not stay quotable as current.*

⛔⛔ **FOUR SCREENS WERE REPORTED AS ORIENTATION-FILTERED AND WERE NOT.** `blastn` searches both
strands, and a transcript carrying the reverse complement of the target window is not a liability in
any degree. `classify()` was given a branch that diverts such hits to
`minus_strand_not_hybridisable`, and the manuscript's Methods stated that orientation was "parsed
and filtered throughout". It was not, in four of the twenty screens the paper counted as filtered:
**TFG e3, e4, e5 and e7** carry `hit_frame` on every hit and were classified *before* the branch
read it, so every minus-strand hit in them is still labelled a cleavage risk. Measured: **83
minus-strand hits counted as `true_cleavage_risk`**, 25 + 26 + 32 across e3, e5 and e7, with e4
contributing none only because none of its four minus-strand hits happened to span the gap.

⛔ **THE DEFECT WAS IN THE DETECTOR, NOT THE CLASSIFIER, AND IT IS THE SAME MISTAKE ONE LEVEL UP.**
`screen_orientation_status()` returned `orientation_parsed` as soon as **any hit carried
`hit_frame`** — it tested that the *field existed*, never that a count had been computed from it.
`classify()`'s own docstring warns in bold that parsing `hit_frame` alone fixed nothing because the
classifier did not read it; the detector then made exactly that mistake about the classifier. **A
populated field is not a measured one.** The audit is now on the labels: a screen is filtered only
if no hit is simultaneously `is_minus_strand: True` and labelled anything other than
`minus_strand_not_hybridisable` (`screen_counts_are_orientation_filtered`).

⚠ **AND THE CONSUMER FAILED OPEN.** `submission_tables.py` decided which rows to mark as
upper bounds with `"UNPARSED" not in status` — chosen deliberately so that an unrecognised value
would be treated as unfiltered, the safe direction. It was not safe. The new state is named
`orientation_parsed_but_labels_are_strand_blind_upper_bounds`, which does not contain that word, so
the sniff answered `True` and four upper-bound rows would have rendered as measurements. **A test
for the absence of one word is not a test for the presence of a property.**

⚠ **THE FOUR SCREENS ARE DEMOTED, NOT REPAIRED, AND THAT IS NOT A CHOICE.** Only the top 15 hits of
a hitlist up to 50 long are retained, so the aligned strand of the truncated tail is gone. An upper
bound is the honest reading and the only available one. They now carry ‡ in Table 2 beside the three
screens that never parsed strand at all and the one that returned nothing.

✅ **THE HEADLINE SURVIVED THE AUDIT UNCHANGED**, which is worth recording because it was not
guaranteed: the four clean designs are all at *TCF12* junctions, none of the demoted screens is a
*TCF12* screen, and re-deriving cleanliness from the corrected corpus returns the same four
sequences at the same three junctions.

| quantity | superseded | current | why it moved |
|---|---|---|---|
| junctions with orientation filtered | 20 | **16** | four demoted by the label audit |
| designs in the filtered corpus | 95 ("five designs at each" of 20) | **75** | the demotion, and three junctions never had five screened designs |
| junctions screened in total | "Twenty" | **24** (+1 that returned nothing) | the paper had been counting only the filtered ones |
| minus-strand share, abstract | 42% | **47%** | 42% pooled over all 27 screens, 7 of which record no strand at all and so contributed denominator without numerator |
| minus-strand share, Results | "half (539 of 1,074)" | **47% (362 of 777)** | 1,074 counted `true_cleavage_risk` + `minus_strand_not_hybridisable`, which admits 94 minus-strand hits whose gap is disrupted and which no classifier would call gap-spanning |
| per-junction range | 0% (TFG e4) to 89% (EWSR1 e7, TCF12 e11) | **4% (TFG e2) to 100% (TCF12 e7)** | the 0% floor was TFG e4, a demoted screen whose filter never diverted anything; the true maximum is TCF12 e7, where every apparent risk is minus-strand |
| EWSR1 e7 / e13 after filtering | "differ by an order of magnitude" | **6 and 53** | unchanged in substance; the counts are now stated |
| designs reaching the 50-hit cap | 25 of 108 | **15 of 75** | 108 matched no corpus: the real-junction total is 105 and the filtered total is 75 |
| designs with untruncated hit lists | 26 of 95 | **24 of 75** | follows the demotion |
| median locus inflation | 2.25 | **2.50** | recomputed over the 24, not the 26 |
| Table 1 title | "across four *NR4A3* fusion partners" | **five** | the table has always listed five and totalled "all 5 partners" |
| TAF15 e6 screen | "not among the 12 reported here" | **one of five designs screened, unfiltered** | it is in Table 2; "12" matched no corpus |

⚠ **Two §3.3 clauses were withdrawn as unsupported rather than restated.** "*TFG* … its other five
range from 5 to 40" described four screens that are now upper bounds plus one (e2) whose minimum is
1. And "three of the eight *TCF12* junctions still score worse than the best FET junction" is false
on the data in either direction: the *TCF12* minima are 0, 0, 0, 1, 1, 1, 1, 1 against a best FET
minimum of 1, so five **match** it and none is worse.

**Pinned by** `research/modalities/tests/test_aso_submission_numbers.py`, which re-derives every
figure above from the committed screens and fails if the manuscript and its evidence diverge again.
Its last parametrised test asserts that none of the superseded values in the left column can
reappear in the running text.

### Appendix B.2 — the graded re-score was computed on hits the oligonucleotides cannot bind

⛔ **THE ORIENTATION DEFECT REACHED THE GRADED MODEL TOO, AND THERE IT INVERTED A HEADLINE.**
`grade_one` scores each retained hit by the residual cleavage a gap-internal mismatch is predicted to
permit, reading `gap_mismatch_histogram` — which `screen_one` writes over **every** ranked hit
*regardless of strand*. So the load was computed partly on transcripts carrying the reverse
complement of the target window, which an antisense oligonucleotide cannot hybridise: no duplex, no
RNase-H1 substrate, nothing to cleave, and therefore nothing to score.

**Measured.** The four designs the paper reports as carrying no hybridisable near-match — at *TCF12*
exons 7, 9 and 17 — have **zero plus-strand near-matches**; every one of their 8, 2, 1 and 7 hits is
minus-strand. Their committed graded artifacts nevertheless reported
`zero_predicted_cleavage_load: False`, with a residual load of 7.2 under the five-fold bound and 8.0
under the pessimistic one, and `n_oligos_with_zero_predicted_cleavage_load: 0` in every graded file.
A reviewer downloading the archive would have found artifacts that appear to refute the manuscript's
headline, and both would have been ours.

⚠ **AND THE GRADED FILES WERE STALE ON TOP OF IT.** `junction-aso-offtarget-tcf12e17n3-graded.json`
carried `n_full_gap_duplex: 7` against its own source screen's `n_true_cleavage_risk: 0` — it was
generated before the screen's classifier was corrected, so re-running was needed independently of
the histogram fix.

| quantity | superseded | current |
|---|---|---|
| designs with zero predicted cleavage load, all real junctions | 0 | **4**, at *TCF12* exons 7, 9 and 17 |
| `-graded.json` files committed | 13 of 25 gradeable screens | **25 of 25** |
| Methods, on the graded re-score | "Every screen was therefore re-scored" | 25 of 27; the two exceptions named (one coverage-only, one with no successfully screened design) |
| residual load, `GGGCATATCTCTATAA` | 7.2 / 8.0 | **0 / 0** |

✅ **THE FIX IS BOUNDED AND FAILS TOWARD THE UPPER BOUND.** The histogram is rebuilt strand-aware
**only where the retained hit list is complete**, because `screen_one` keeps the strongest 15 of a
hitlist up to 50 and the strand of a truncated tail is unrecoverable. A censored design keeps its
strand-blind histogram and its load stays the upper bound it always was; every graded row now records
which of the two it is (`gap_histogram_orientation_filtered`).

⚠ **A ZERO HERE IS ARITHMETIC, NOT A MEASUREMENT**, and the manuscript says so where it reports it: a
design with no hybridisable hit to score has zero load under any discrimination bound, which is
weaker than a bound-specific finding. What it does establish is that the harsher of the two bounds
does not move these four, because there is nothing for it to act on.

⭐ **THE TRIPWIRE THAT CAUGHT THIS WAS OUR OWN, AND IT WORKED.**
`test_no_design_at_any_real_junction_reaches_zero_predicted_cleavage_load` asserted `n_zero == 0` and
its docstring said a non-zero count would mean "the manuscript's central claim has changed". It
tripped, for the right reason. It is now
`test_exactly_the_four_orientation_clean_designs_reach_zero_predicted_cleavage_load`, still a
tripwire and pointed the other way: a fifth design reaching zero, or any design outside those three
junctions, fails the build — because with the strand filter correct, the only remaining route to a
zero is a censored design whose unseen tail was assumed away. A second test asserts directly that no
design with even one hybridisable hit is ever awarded a zero.

### Appendix B.3 — full junction coverage, and the partner effect it dissolved (2026-08-13)

⭐ **THE CORPUS WENT FROM 16 ORIENTATION-FILTERED JUNCTIONS TO 37, AND ONE REPORTED FINDING DID NOT
SURVIVE IT.** Twenty-two junctions were screened in a single evening — the eight whose earlier
screens had never applied the orientation filter, and the fourteen that had never been screened at
all — taking coverage to all 38 frame-compatible junctions.

⛔ **WHAT FELL: "BREADTH AND SPECIFICITY POINT AT DIFFERENT PARTNERS."** Over the partial corpus every
design with no hybridisable near-match was at *TCF12*, and the manuscript reported that as a partner
effect: the multi-partner reagent is a FET one, the clean designs are not. With all 37 filtered
junctions in hand, **every one of the five partners has a junction whose best design carries no
hybridisable gap-spanning near-match** — three of eight at *TCF12* and at *FUS*, two of eight at
*EWSR1*, one of eight at *TAF15*, one of five at *TFG*. The effect is gone.

⚠ **AND NOTHING ABOUT *TCF12* CHANGED.** The comparison had been drawn against partners whose
junctions were mostly unscreened, and an absence of clean designs among junctions nobody had
screened is not evidence that clean designs are absent there. This is the same error shape as
`screen_orientation_status` reading field presence as filtering: a property inferred from what had
not been looked at.

| quantity | superseded | current |
|---|---|---|
| orientation-filtered junctions | 16 | **37** |
| designs in the filtered corpus | 75 | **178** |
| junctions with any screen | 24 of 38 | **38 of 38** |
| minus-strand share | 47% (362 of 777) | **46% (738 of 1,610)** |
| junctions at 100% minus-strand | 1 (*TCF12* e7) | **2** (*EWSR1* e1 and *TCF12* e7) |
| designs with no hybridisable near-match | 4, at 3 *TCF12* junctions | **9, at 6 junctions across 4 partners** |
| designs at the 50-hit cap | 15 of 75 | **30 of 178** |
| right-censored designs | 51 | **131** |
| uncensored designs | 24 | **47** |
| median locus inflation | 2.50 (max 7.0) | **2.20 (max 11.0)** |
| unscreened frame-compatible junctions | 14 | **0** |

✅ **WHAT SURVIVED UNCHANGED, WHICH IS THE USEFUL CONTROL.** The per-junction minus-strand range is
still 4% to 100%; *EWSR1* exons 7 and 13 still return 55 and 57 apparent gap-spanning hits and still
stand at 6 and 53 after filtering. Those are the numbers the orientation argument rests on, and more
than doubling the corpus did not move them.

⛔ **A DISCREPANCY WORTH KEEPING VISIBLE: THE GRADED MODEL HAS NO CENSORING GUARD.** Ten designs score
zero residual cleavage load; only nine are reported clean. `GCATATCTCCTCGCCC` at *FUS* exon 11 returns
21 near-matches of which 15 are retained, all minus-strand — so `grade_one` sees nothing hybridisable
and awards zero, while the cleanliness criterion refuses it because the six unretained hits are
unknown. The stricter count is the one the manuscript reports, and the gap is asserted in
`test_junction_aso_graded.py` rather than filtered out.

⚠ **ONE JUNCTION IS STILL UNFILTERED: *TFG* exon 4.** Its re-screen was in the batch that lost a push
race to `modalities-cache` — six concurrent jobs, four winners — and the pre-existing strand-blind
file remained. **The lesson is about the CHECK, not the race:** the coverage test asked whether the
artifact existed, and the stale file satisfied it. File presence is not file correctness, which is
the third time this session that a check keyed on existence rather than on the property it cared
about produced a false pass.

### Appendix B.4 — coverage completed (2026-08-13)

✅ **ALL 38 FRAME-COMPATIBLE JUNCTIONS ARE NOW ORIENTATION-FILTERED.** *TFG* exon 4 — the last
exception, left behind when its re-screen lost a push race and the pre-existing strand-blind file
satisfied a coverage check that asked only whether the file existed — was re-screened and folded in.

| quantity | superseded | current |
|---|---|---|
| orientation-filtered junctions | 37 of 38 | **38 of 38** |
| designs in the filtered corpus | 178 | **183** |
| minus-strand share | 46% (738 of 1,610) | **44% (738 of 1,677)** |
| per-junction range | 4% (*TFG* e2) to 100% | **0% (*TFG* e4) to 100%** |
| designs at the 50-hit cap | 30 of 178 | **35 of 183** |
| right-censored designs | 131 | **136** |

⭐ **THE NUMERATOR DID NOT MOVE — 738 BOTH TIMES — AND THAT IS THE POINT.** *TFG* exon 4 contributes
67 apparent gap-spanning hits and **not one of them is minus-strand**, which is why it now sets the
floor of the per-junction range at 0%. It is the only junction in the corpus with no minus-strand
gap-spanning hit at all, and its earlier strand-blind labels were therefore, by coincidence, not
over-counting anything. That is luck rather than vindication: the same defect on any other junction
inflated its counts, and nothing in the stale artifact distinguished the two cases.

✅ **UNCHANGED BY THE ADDITION:** nine clean designs at six junctions across four partners, median
locus inflation 2.20, and every partner still having a junction whose best design is clean. The
last junction closed a coverage gap without moving a headline.

### Appendix B.5 — the pre-mRNA compartment, measured (2026-08-13, run 31697045904, $0)

⭐ **THE PAPER'S OWN LARGEST STATED BLIND SPOT IS NOW A READING RATHER THAN A CONCESSION.** Its
Limitations had said, unchanged for as long as the section existed, that both screens search mature
transcript only, that RNase-H1 is nuclear, that intronic and intron–exon-spanning sites are therefore
invisible to both, and that "that gap is closable by a genomic screen and is not closed here." A
repository-wide grep for `genomic screen` on the morning of 2026-08-13 returned **exactly that one
sentence** — no `required_validation` row, no method-watch entry, no item in this record. A conceded
hole is the easiest kind to keep, because conceding it reads as rigour.

⚠ **AND THE OMISSION WAS NOT NEUTRAL IN ITS DIRECTION.**
[`hybrid-intron-aso-target.md`](hybrid-intron-aso-target.md) already said so for the same database
families: both target sets are mature-transcript sets, so "running them unchanged yields a low
off-target count **by construction**." A junction gapmer's two halves are both exonic, and in a parent
pre-mRNA an exon is followed by an intron rather than by the next exon — so parent pre-mRNA is exactly
where a design's donor half sits beside sequence no mature screen has ever compared it against.

**What ran.** [`aso_premrna_offtarget.py`](../../modalities/aso_premrna_offtarget.py) → 
[`aso-premrna-offtarget.json`](../../modalities/aso-premrna-offtarget.json). Unspliced sequence and
exon coordinates for all six parent transcripts, retrieved from Ensembl; every one of the 190 designs'
target windows scanned against all of it at ≤2 mismatches — **derived** from
`MAX_MISMATCHES_PER_NEAR_MATCH` rather than typed, because a stricter threshold here would return a
cleaner pre-mRNA result for that reason alone — both orientations, gap-resolved, and each hit
classified as wholly intronic, wholly exonic, or spanning an intron–exon boundary.

| reading | value |
|---|---|
| designs scanned | 190 |
| with any pre-mRNA near-match, either orientation | 53 |
| with a hybridisable, gap-fully-paired site | 19 |
| of those, sites no mature screen could see | 19 of 19 |
| intron–exon-spanning sites, all in *NR4A3* | 9 |
| wholly intronic sites, all in *TCF12* | 10 |
| intronic nucleotides searched | 517,157 (*TCF12* is 365,096 of them, 71%) |

⭐ **THE NINE NR4A3 SITES ARE THE FINDING, AND THEY ARE MECHANISTICALLY NECESSARY RATHER THAN
COINCIDENTAL.** Every one sits six or seven nucleotides into *NR4A3* intron 2, spanning the boundary
into exon 3 — verified against the committed exon spans, not inferred. A junction gapmer's acceptor
half **is** the 5′ end of *NR4A3* exon 3, and the wild-type transcript reaches that same exon across
its own splice junction, so a design whose donor half also matches the 3′ end of intron 2 within the
mismatch budget pairs across the real splice site. ⛔ **That is a route to wild-type *NR4A3*
engagement that does not pass through the fusion at all, in the compartment where RNase-H1 is active,
and gap-level discrimination cannot protect the parent there because the gap is fully paired.** It is
the discrimination question this program exists to answer, arriving from a direction nobody had
screened.

⚠ **THE TEN *TCF12* SITES ARE A LENGTH EFFECT AND ARE REPORTED AS ONE.** *TCF12* holds 71% of the
intronic sequence searched and 100% of that class; 7 of 10 would be expected from volume alone. It
says nothing about *TCF12*.

✅ **TWO THINGS THIS CHANGED FOR THE PAPER'S OWN CLAIMS.** The gap-level margin predicts the
liability — 12 of 76 designs at margin 1, 7 of 76 at margin 2, **none of 38 at margin 3** — so a
third independent instrument now orders the candidates as the base count and the free energy already
did. And **none of the nine designs the cleanliness claim rests on carries a pre-mRNA site**, so that
claim survives the compartment it could not previously see. Neither outcome was arranged: the screen
was written before either was known, and the artifact is what decided them.

⚠ **SCOPE, STATED RATHER THAN IMPLIED.** Exhaustive over six parent transcripts and nothing else. The
other ~20,000 genes' introns remain outside all three screens, and this arm inherits the
substitution-only bound — complete for mismatches by construction, blind to insertions and deletions.
The module carries a best-effort genome-wide NCBI arm behind `PREMRNA_GENOMIC=1`; it has not been run,
and the artifact records that it did not rather than leaving the field absent.

✅ **AND IT IS THE ONE SCREEN IN THE PAPER THAT RECOMPUTES WITH NO NETWORK AT ALL.** The retrieved
sequence and exon coordinates travel with the archive, so `--offline` against the committed cache
reproduces every number above; verified bit-identical before the result was written up. The other two
arms need NCBI BLAST and a RefSeq download.

### Appendix B.6 — the censoring guard, tested (2026-08-13, run 31697971910, $0)

⭐ **THE RESTRICTION THE HEADLINE DEPENDS ON WAS AN ARGUMENT UNTIL TODAY, AND IT IS NOW A READING.**
A design is not called clean merely because its RETAINED hits are all minus-strand: the strand of an
unstored hit is unrecoverable, so a truncated list cannot establish that nothing hybridisable remains.
That restriction is what separates **nine designs at six junctions** from **twenty-four at eighteen**,
which is the single most inviting overstatement available in this paper — so whether it is cautious or
merely conservative matters.

**The population.** Seven design-and-junction records have no hybridisable retained hit AND a raw
count above the retention depth but below BLAST's own 50-hit ceiling, so **retention alone** is what
withholds a verdict on them. They were re-screened at `BLAST_HITLIST_SIZE=500`,
`SAVED_HITS_PER_DESIGN=500` under the suffix `-deep500`.

| design | junction | shallow (raw / stored / hybridisable) | deep (raw / stored / hybridisable) | verdict |
|---|---|---|---|---|
| `GCATATCTCCTCGCCC` | *FUS* e11 | 21 / 15 / 0 | **161 / 161 / 5** | not clean |
| `CAGGGCATATCTCCTC` | *FUS* e11 | 47 / 15 / 0 | **196 / 196 / 119** | not clean |
| `CAGGGCATATCTCCTC` | *TAF15* e14 | 47 / 15 / 0 | **196 / 196 / 119** | not clean |
| `GGGCATATCAGCATCT` | *TAF15* e9 | 23 / 15 / 0 | **68 / 68 / 48** | not clean |
| `AGGGCATATCTAGAAT` | *TCF12* e11 | 27 / 15 / 0 | **65 / 65 / 5** | not clean |
| `CAGGGCATATCTAGAA` | *TCF12* e11 | 35 / 15 / 0 | **78 / 78 / 10** | not clean |
| `GCATATCTCCACCTCC` | *FUS* e5 | 41 / 15 / 0 | screen failed at the remote service | undecided |

⛔ **SIX OF SEVEN DECIDED, AND NOT ONE IS CLEAN.** Every design that looked clean over its retained
window turns out to carry hybridisable near-matches once the window is opened — one of them **119** of
them. The shallow counts were not merely bounds but severely censored ones: 21 against a true 161, 47
against 196. **Relaxing the guard would have promoted six records the evidence refutes**, and the nine
are unchanged by the test.

⚠ **THIS IS A SEPARATE MEASUREMENT, NOT A CORRECTION.** A count taken at a deeper ceiling is a
different instrument reading; it does not revise the shallower corpus, and **no number in the
manuscript is restated from these artifacts.** They are released under their own suffix for exactly
that reason.

⚠ **WHAT IS STILL BOUNDED.** Eight further records sit AT the 50-hit ceiling, where the bound is the
search's own cap rather than retention, and were not re-screened. Seven designs' original queries
failed at the remote service and are still unscreened. Both are registered on `RT-ASO`.

### Appendix B.7 — the genome-wide arm, attempted and not interpretable (run 31698435645, $0)

⚠ **REPORTED BECAUSE A FAILED ATTEMPT IS A READING TOO.** The nine clean designs were queried against
the public NCBI URL service for a genomic database. It answered on **`core_nt`** — a mixed corpus of
genome assemblies, BAC clones, patent sequences, immunoglobulin isolates and RefSeq transcripts, not a
genome reference. **All nine queries saturated the 50-hit ceiling** (one returned 52), and the returned
identities run down to 13/16, below the ≥14/16 threshold this work admits. The counts therefore
separate nothing, and no claim rests on them.

⛔ **THE MODULE REFUSES TO DEGRADE INTO A TRANSCRIPT SEARCH UNDER A GENOMIC LABEL**, which is why
`refseq_rna` is not in its candidate list and must not be added: a mature-transcript database returning
a clean answer under the name "genomic screen" would reproduce, with a provenance string asserting the
opposite, the exact defect the pre-mRNA work exists to close. A real genome-wide screen needs a local
BLAST database rather than the public URL API. Recorded so nobody repeats the attempt.

### Appendix B.8 — the locus-parser correction reaches the manuscript, and four other stale numbers (2026-08-13, $0)

⛔ **`locus_of` WAS FIXED IN `5233cf867` AND ONLY ONE OF THE MANUSCRIPT'S LOCUS COUNTS WAS RECHECKED.**
The parser split the RefSeq definition on the first comma, so every gene whose own description carries
one degraded to one accession fallback per variant. The fix landed with the collapse artifact
regenerated and the lead reagent's §3.7 figure corrected; **every other locus count in the paper was
still the old parser's.** Recomputed here from the committed artifacts, all superseded values retained:

| where | superseded | measured now | why it moved |
|---|---|---|---|
| §3.2, *TAF15* e6 | four loci at best, **seven** for the margin-leader, **five of seven** predicted-only (default depth, Table 2) | **three** at best (`AGGGCATATCTTGTGT`), **five** for the margin-leader `GGGCATATCTTGTGTG`, **three of five** predicted-only, at the deeper ceiling (Table 4) | old parser, and three of the five designs are truncated at default depth so the sentence quoted bounds as minima |
| §3.3, *TCF12* e5 | "the highest gap-spanning near-match load in the panel: **17 loci**, 12 of them predicted" | **17 gap-spanning near-matches at ONE curated locus, `PIK3CG`** — and not the panel's highest load | `phosphatidylinositol-4,5-bisphosphate …` carries a comma, so seventeen PIK3CG variants became seventeen fallbacks |
| Table 2, *TAF15* e6 | `11 → 10` loci, 7 gap-spanning loci, 5 predicted-only | `11 → 7`, **4**, **2** | ditto |
| Table 2, *EWSR1* e9 | `29 → ≥10` loci | `29 → ≥2` | ditto |
| Table 2, *TCF12* e5 | `26 → ≥15` loci, 12 predicted-only | `26 → ≥1`, **0**, gap-locus column now `≤17` | ditto |
| §3.6 | "**23 designs** … 20 of the 23 had not approached the cap" | **164 of the 180** designs screened at both depths, **129** not at the cap | population not reproducible from the artifacts; the deep corpus grew to 187 records after it was written |
| Limitations | "**141 of 157** comparable designs … **125** of those" | same measurement as §3.6, stated once | ditto |
| §4 | "0.69 times the expected number of **exact** genomic matches" | 0.69 is the **≤2-mismatch** ratio; the exact ratio for that design is **0.73** | the label was wrong, not the number — §3.8 uses the same (le2, gap-paired) pair correctly |
| §4 | "**Two** designs survive every screen applied here" | **three**, two of them at any parent-duplex threshold | §3.8 and the abstract already said three; §4 disagreed with both |
| Methods | "39 of the **45** screens released in total … and the **five** deeper re-screens" | **39 of 78**; the ungraded set is the **38** deep re-screens plus one coverage-only control | the deep corpus grew from 5 junctions to 38 while the graded count, 39, never moved |
| §3.4 | "**twenty-two** of them screened or re-screened after alignment strand was parsed" | clause removed | the figure has no home in any artifact — 21 junction screens carry the post-fix orientation field, not 22 — and it read as if the other 16 were unfiltered, which the corpus test refutes |
| Limitations | "nothing here bounds what a longer catalytic gap would achieve at the same seams" | "every result reported here is specific to that geometry" | the negative is no longer true; longer-gap geometries at these seams are under separate measurement and nothing is claimed about them here |

⚠ **THE SCREEN ARTIFACTS STILL CARRY THE OLD PARSER AND CANNOT ALL BE FIXED OFFLINE.**
`_locus_summary` is computed at screen time over the COMPLETE ranked hit list, and only the top 15 are
stored, so for a truncated design the exact count is unrecoverable without re-running BLAST.
`collapse_oligo` now prefers its own recount wherever the stored list is complete — exact and current —
and falls back to the frozen figure only when truncated, where Table 2 marks it `≤` because the old
parser can only over-count. Measured across every committed screen: 33 of 236 uncensored records
disagreed with the frozen field, worst `TAF15` e4 / `GCATATCTGACTGACT` at 95 against a true 8.

⛔ **AND THE FROZEN FIELD IS WHY THIS SURVIVED THE FIX.** The collapse artifact WAS regenerated in
`5233cf867`, so `n_distinct_loci` and the predicted-only counts became current in the same commit —
while `n_loci_with_a_gap_spanning_hit`, the one column §3.2, §3.3 and Table 2 actually quote, kept
reading a value frozen inside the screens. A regeneration that updates two of three columns looks
exactly like a regeneration that updates all three.

⭐ **WHAT WAS CHECKED AND FOUND CORRECT**, so it is not re-litigated: the lead reagent's §3.7 and §4
figures (189 near-matches, 141 hybridisable, 123 gap-paired, six loci, `ANKS1B` + `ZNF667` 104, 82 of
123 predicted, no parent); the 2.25 median inflation over 44 designs and its 11.0 maximum; every
§3.5 deep count (27, 29, 84; 64, 14, 11; 8→118; 7→67); the five clean-design parent duplexes and the
zero pre-mRNA sites among the nine; the genome strata (236 exact against 1.37 expected, 0.98 median
ratio, 14 above twice, 52.5 % against 51.4 % masked, 20 of 176 with a named gap-paired site); and
every §3.9 thermodynamic and design-rule figure.

### Appendix B.9 — the gap-length screen enters the manuscript, and the pooling it nearly caused (2026-08-14, $0)

⭐ **THE RESULT.** The 5-6-5 panel was tiled and screened again at 5-8-5 and 5-10-5 over the same
seams, wing held at five nucleotides. Inside the catalytic gap the junction-unique bases on the
shorter side and the bases one wild-type parent pairs on the longer side are **complements summing
to the gap** — asserted for all 798 designs in `aso-gap-length-tradeoff.json`, not assumed — so each
nucleotide of gap-level margin gained is a nucleotide of contiguous wild-type-parent duplex
conceded. That is now §3.10 and Table 5, and it sharpens the Conclusions rather than overturning
them: the limiting step remains fusion-versus-parent discrimination at the gap, and gap length is
shown to be unable to relieve it by construction.

| where | superseded | measured now | why it moved |
|---|---|---|---|
| Limitations | "One architecture was tiled, a 16-mer 5-6-5, so **every result reported here is specific to that geometry**" | §3.10's result, with its own bounds stated | placeholder written while these numbers were still moving; the geometries are now screened and reported |
| Methods | "39 of the **78** screens released in total … and the **38** deeper re-screens" | **39 of 93**; the ungraded set is **53** deep re-screens plus one coverage-only control | 15 further deep screens released at 5-8-5 (7) and 5-10-5 (8); the graded count, 39, has never moved and so the sentence kept reading as current at 45, at 78 and at 93 |

⛔ **THE MERGE ALMOST POOLED THREE GEOMETRIES INTO EVERY 16-MER POPULATION, AND NOTHING WOULD HAVE
SAID SO.** The new screens are written under the same `junction-aso-offtarget-*` and
`aso-insilico-evaluation-*` globs the manuscript's own generators read. Measured on merging, before
any fix:

| generator | what a regeneration would have done |
|---|---|
| `junction_aso_locus_collapse.py` | deep population 38 screens / 187 designs → **53 / 303**; `oligos_with_no_gap_spanning_locus` **12 → 110**, which reads as a panel an order of magnitude cleaner and is only a wider glob |
| `aso_per_junction_table.py` | the six re-screened junctions **5 designs → 21**, and `best_available` at the *EWSR1* e12, *FUS* e10 and *TAF15* e11 seams moved off the 16-mer this paper reports onto an 18-mer — scored against `GAP_REGION_1BASED`, which is 5-6-5's `(6, 11)`, so six of that design's eight catalytic bases were counted as its whole gap |
| `offtarget_chance_baseline.py` | refused to build at all, correctly: an 18-mer panel of a seam grouped with the 16-mer panel of the same seam and the counts disagreed |

**This is the depth defect one axis out.** `5233cf867` had already established that *depth* is part of
a screen's identity and must not be pooled away, after a widening glob moved a manuscript-quoted
median from 2.14 to 4.55 with no science behind it. Geometry is part of it for the same reason and
with a sharper edge, because the gap region is a module-level constant: pooling geometries does not
merely mix populations, it measures a longer design's catalytic gap with a shorter one's window.
Each generator now partitions on the oligonucleotide length **measured from the designs themselves**,
never from a filename, since screens committed before 2026-08-13 carry no geometry block to read.
The excluded screens are named in each readout rather than dropped silently, and the chance
baseline's grouping key became `(seam, geometry)` — two panels are re-emissions of one another only
if they screened the same seam with the same reagent.

⚠ **ONE FIGURE IN THE HAND-OFF BRIEF HAS NO HOME AND WAS NOT USED.** The brief reported accessibility
as flat across the geometries at 0.446 / 0.460 / 0.428. No such quantity exists in
`aso-gap-length-tradeoff.json` or in any committed artifact — the evaluation panels record an
accessibility *window* (`status`, `window_len`, `window_mRNA_span`) and no per-design or per-geometry
figure — so nothing about accessibility is claimed in §3.10. The hypothesised cost it would have
removed is simply left open.

⭐ **WHAT WAS RE-DERIVED AND FOUND UNCHANGED**, so it is not re-litigated: every default-depth 16-mer
count in the paper, `totals_over_uncensored_oligos_only` and the deep totals of the collapse
artifact, all 38 rows of Table 4, and `offtarget-chance-baseline.json` byte-for-byte. The only
committed value the merge moved was the recorded `transcriptome_nt_source`, which had begun naming
an 18-mer panel for a 16-mer corpus's span; the span itself, 718,571,139 nucleotides, is unanimous
across all 13 panels that record it and did not move.

### Appendix B.10 — the wild-type NR4A3 liability argument, withdrawn from the Introduction (2026-08-14, $0)

⛔ **THE CLAIM DOES NOT FOLLOW FROM THE CITED PHENOTYPE, AND IT IS OUT (trimcrae, 2026-08-14:
*"You need NR4A1 also knocked out for the leukemia … so it is feasible in principle to knock out
NR4A3 and be fine."*).** The submission's Introduction argued that wild-type NR4A3 is a protein a
therapy should not silence indiscriminately, and rested it on Mullican (PMID **17515897**) plus the
context-dependent-roles review (PMID **33106376**). Mullican's phenotype is the **combined**
*Nr4a1*⁻/⁻;*Nr4a3*⁻/⁻ mouse; single nulls do not develop AML, which the repository already records as
a hard constraint on the *degrader* route for exactly the opposite reason — the degrader
reconstitutes the pair, an ASO against the junction does not
([roadmap](../nr4a3-program-map.md), [`target-route-options.md`](../program/target-route-options.md)).
Read as a bound on losing NR4A3 alone, the citation is being asked to carry a paralogue-redundancy
question it does not answer: NR4A1 and NR4A2 are the plausible replacements, and nothing retrieved
here measures whether they suffice. The review's context-dependent roles are weaker still — they
establish that the direction varies by tissue, not that chronic systemic loss is harmful.

**Withdrawn text**, registered here so it stays quotable as history and nowhere else:

> That matters because NR4A3 can be tumour-suppressive. Combined *NR4A1*/*NR4A3* loss causes acute
> myeloid leukaemia in mice, and NR4A3's roles in cancer are context-dependent, tumour-suppressive in
> some tissues and tumour-promoting in others. Either way, wild-type NR4A3 is not a protein a therapy
> should silence indiscriminately.

⚠ **WHAT THIS DOES AND DOES NOT COST THE PAPER.** It removes an argument, not a measurement. Nothing
in Results, §5 or §6 rested on it: every parent-screen count is a **selectivity** finding, and a
design that pairs its catalytic gap against wild-type *NR4A3* is a design that is not
junction-selective, which is the paper's subject whether or not losing NR4A3 is tolerable. The same
screens' *EWSR1*, *TAF15*, *FUS*, *TCF12* and *TFG* liabilities are untouched by this and were never
argued from NR4A3 biology. PMIDs 17515897 and 33106376 leave the submission's reference list, which
falls 35 → 33; superscripts were re-derived by `submission_citations.py --write` rather than
renumbered by hand.

⭐ **IT ALSO CLOSES A KNOWN CONTRADICTION.**
[`emc-treatment-strategy.md`](../program/emc-treatment-strategy.md) had logged, as an open
pre-submission item, that the repository asserted both "WT NR4A3 loss is tolerable (paralogue
redundancy)" for the degrader and "sparing WT NR4A3 avoids the tumour-suppressor liability" for the
ASO, and that as two independent confident claims they contradict. The ruling resolves it in the
first direction: **tolerability is unresolved, and neither manuscript may claim the liability as
established.** The ASO's wild-type sparing is now stated as what it is, a fusion-versus-wild-type
selectivity property the LBD degrader cannot offer.

---

## 2026-08-13 · Folding the off-target expression read into the paper (§3.11, Table 6)

The expression branch answers a question no screen in this paper had asked: the screens establish
that a design matches a gene, never that the gene is transcribed where the drug goes. Folded in as
§3.11, a Methods paragraph, one paragraph of §4 and **Table 6**, which is generated from
`aso-offtarget-tissue-expression.json` so a cell and its source cannot diverge.

⚠ **THE HAND-OFF BRIEF DESCRIBED THE *TAF15* REAGENT'S LOAD AT SEAM LEVEL, AND THE MANUSCRIPT NEEDED
IT AT REAGENT LEVEL — THE TWO DIFFER BY MORE THAN THREEFOLD.** The brief reported "six of seventeen
seam loci reach the exposure organs" against the reagent 5′-GGGCATATCTTGTGTG-3′. Those 17 loci belong
to the **seam**, which is tiled by five designs; the named reagent returns **five** of them, of which
**one** (*NRP1*) reaches the upper cut. Written as the brief framed it, §4 would have attributed to a
molecule a load that is a property of the window it was slid through. Both §3.11 and §4 are pinned
per design by `_loci_of_design` in `test_aso_submission_numbers.py`, which exists for this reason.
The same brief ranked *NRP1* "eleventh of seventeen" by record count; sorted on
`n_transcript_records` it is **seventh** (56, 22, 18, 13, 12, 10, **5**, …). Neither figure was used.

⭐ **THE TWO-ROUTE GTEx AGREEMENT IS REAL AND IS DELIBERATELY NOT IN THE PAPER.** Two committed
artifact revisions read the exposure column by different routes — `f74328f93` via
`portal_api_v2_fallback`, `8579a4847` via `release_gct`, both after the tissue-key fix. Re-derived
here: **48 locus × exposure-tissue pairs, 43 identical, worst relative difference 1.97 × 10⁻¹⁴ %**.
⚠ The brief's denominator of **57** counts the 19 `arm_a_gtex.rows` gene-model rows × 3 tissues, not
the 48 per-locus readings. It is omitted from the manuscript on merit rather than for length: it is a
transport check on one underlying release reached two ways, it is explicitly **not** a second
measurement of the biology, and no committed artifact carries the comparison as a field — the current
artifact records `url_attempts` of length 1 and one endpoint.

⛔ **A LATENT DEFECT SURFACED BY RUNNING THE CHAIN, LEFT UNFIXED AND UNCOMMITTED ON PURPOSE.**
`scripts/regenerate_aso_chain.sh` step 0 rescores every screen it finds, which generates **53
`-graded.json` artifacts for the deep and gap-length screens that have never been committed** — the
committed manifest carries 352 files and **zero** deep-graded entries. Materialising them changes
Table 3: `_graded_loads` in `submission_tables.py` keys on `(source_screen, sequence)` and carries
**no depth**, so for 5′-GGGCATATCTCTATAA-3′ at *TCF12* e17 the default screen's `0 / 0` and the
deep screen's `31.4 / 101` collapse into one cell reading `31.4 / 101 / 0 / 0`. Table 3 is by its own
legend the **default-depth** result, so that cell mixes two populations, and the `/`-joined format
was built to show the two *discrimination models* disagreeing, not two depths. This is the
2026-08-13 depth defect one consumer further on, in the one generator the geometry sweep fixed for
geometry and not for depth. The 53 artifacts were **removed rather than committed** and the manifest
re-derived at 352 files, so this branch carries the expression work only; the fix changes a
submission table's semantics and is trimcrae's to sequence.

✅ **CLOSED 2026-08-14, AND THE RULING ON THE 53 IS: DO NOT COMMIT THEM.** The Methods already say
so — *"all 38 junction screens, and 39 of the 93 screens released in total … and the 53 deeper
re-screens, which are released ungraded"* — and
`test_the_released_screen_and_graded_counts_are_the_ones_on_disk` asserts that inventory against the
tree. Committing them would take `39` to `92` and falsify a sentence in the paper, so the question
was settled by the manuscript rather than by preference. **What was actually wrong is that two
consumers changed their output depending on whether those files happened to be on disk**, and both
are now invariant to it:
- **Table 3** selects default depth through the loader (`select=ass.is_default_depth`), the same way
  it already selected one geometry. Verified both ways: with all 92 graded artifacts present the
  regenerated tables file is **byte-identical** to the committed one.
- **The archive manifest** deposits **tracked files only**. It had been globbing the filesystem, so a
  chain run made it hash the 53: measured on this branch at `301873b1d`, `n_files` went **352 → 405**
  and 53 untracked files were listed with SHA-256s **in a pushed commit** before being reverted by
  hand at `963488e90`. A deposit whose rows are in no revision cannot be checked out, which is step 1
  of its own instructions. `gap_resolved_screens_with_no_committed_graded_rescore` now asks git
  rather than `os.path.exists`, so it keeps naming all 53 instead of emptying the moment they appear.

⛔ **THE TRAP IN THIS FIX, RECORDED BECAUSE IT WOULD HAVE LOOKED LIKE A FIX.** `aso_screen_sets.is_deep`
read `artifact["method"]["parameters"]` and `artifact["oligos"]` — the shape of a **BLAST screen**. A
graded re-score has neither key, so it fell through to `max(…, default=0) > 15` and returned **False
for every graded artifact ever written**: 77 sixteen-mer graded artifacts all reading default-depth,
derived from 78 sixteen-mer screens of which 38 are deep. Passing `select=is_default_depth` on top of
that would have kept all 92, moved nothing, and read as correct in the diff. So depth is now measured
per family (`Family.depth_evidence`), `grade_panel` carries the source screen's depth **evidence**
into each re-score the way it already carried its geometry, and `is_deep` **raises** where it cannot
read instead of voting "default" — including for design-evaluation panels, which are exhaustive scans
with no depth axis at all and for which the answer is neither true nor false.

⚠ **Two smaller things found in the same pass.** The manifest's three `junctions_*` fields held
**filename tags**, not junction labels (`taf15e11n3-18mer-deep500-b2` as a "junction"); they now hold
the `junction_label` each artifact states, all three read `[]`, and the vocabulary is asserted rather
than conventional. And `scripts/regenerate_aso_chain.sh` never ran `aso_figure_provenance.py`, so a
chain that moved a figure input printed `ASO CHAIN OK` and left preflight red — it is now a chain
step.

⚠ **`aso_archive_manifest.py --check` IS RED ON EVERY COMMITTED TREE, BY DESIGN — DO NOT CHASE IT.**
The hand-off for this session flagged the manifest as failing `--check` with a stale `git_revision`
before any edit, and regenerating it appears to clear the red. It clears only in the window between
regenerating and committing: the manifest embeds `git_revision`, is generated *before* the commit
that carries it, and so names its own parent the moment it lands. Measured here — regenerated at
`0e37a12bf`, committed as `c6668cb4b`, `--check` red again immediately, with `git_revision` and
`git_tree_is_clean_apart_from_this_manifest` the only two fields differing. The generator says so
itself at the `git_revision` field: it *"moves on every commit, including commits that touch no
archived file, so `--check` goes red after any commit and must NOT be wired into preflight as a
gate"* — which is why preflight is green while this is red, and why the chain script's `--check`
inherits the red. **`archive_content_digest` is the archive's real identity** and is stable across
commits that leave the files alone; it did not move here. The pointer was still worth correcting in
a follow-up commit, because step 1 of the manifest's own deposit instructions is "check out the
revision named in `git_revision` and confirm `git status` is clean", and the revision it named was
one where the recorded hashes do not hold.

**Length.** The paper went 9,303 → 9,754 main words (**+451**). Paid for by deleting a Methods
restatement inside §3.8 and a thrice-stated arithmetic caveat in Limitations, and by keeping the
instrument's method and every caveat in Table 6's legend, which lives in the companion tables file
and costs no main words. Three further trims were **reverted**: `test_unfiltered_screens_are_disclosed_and_counted`,
`test_the_gap_length_trade_is_an_identity_and_the_paper_states_it_as_one` and
`test_the_paper_states_the_two_bounds_that_make_the_fall_partly_arithmetic` each failed on them, and
the last one's docstring says in terms that it exists to stop an edit for length dropping that bound.
The guards were right; net zero was not reachable without cutting honest content.

---

## Correction, 2026-08-15 — "cleanest for once" was a misreading of the exon-2 screens

⛔ **Commit `cf24273fc` records that the deep screens at `EWSR1_e13__NR4A3_e2` and
`TAF15_e6__NR4A3_e2` produced a cleaner result than predicted, and that "the expected result did not
arrive". Both statements are wrong, and this is the correction.**

The recorded prediction was **0 of 5 designs clearing the transcript BLAST**, on the shared *NR4A3*
exon-2 5′UTR acceptor half that both sibling junctions already carried. **The result is 0 of 5 at
both seams.** The prediction arrived exactly.

What actually differs is the *magnitude* of the best design's load — 25 gap-paired hits over 6 loci
at the *EWSR1* seam, against 51–170 at the siblings. **Twenty-five gap-spanning, cleavage-competent
hits is not clean; it is the least dirty of five dirty designs.** Reading a smaller number as a
different *kind* of result is precisely the error the locus-recount and censoring rules in this lane
exist to prevent, and it was made in prose one message after insisting on that distinction.

⚠ The commit message cannot be amended — it is pushed and other work is built on it — so the
correction lives here, per CLAUDE.md rule 1.2 (corrections go in an appendix, not inline).

**What stands from that commit**, all verified before the counts were read rather than after: seam,
`measured_junction`, mode and waiver match the derivation at both junctions; 5 of 5 screened; and
`n_gap_mismatch_unresolvable = 0` across all ten designs, so nothing is right-censored and no
unresolved hit is sitting in these totals reading as a clean one.

| junction | best available | margin | gap-paired | loci | hybridisable | pre-mRNA | genome o/e | wild-type allele |
|---|---|---|---|---|---|---|---|---|
| `EWSR1_e13__NR4A3_e2` | `AGTGGGCTCTCCACGG` | 3 | 25 | 6 | 40 | 0 | 0.657 | clean |
| `TAF15_e6__NR4A3_e2` | `AGTGGGCTCTTGTGTG` | 3 | 128 | 6 | 218 | 0 | 1.206 | clean |

⚠ **And the *TAF15* pick is not the lowest hit count** — `GCAGTGGGCTCTTGTG` has 38 against 128. The
ranking key was read rather than inferred: parent liability, then pre-mRNA, then **distinct loci**,
then margin, with raw hits deliberately last so they cannot reintroduce the isoform inflation the
locus recount exists to remove. The chosen design touches 6 loci against 13. Not a bug.

**Coverage is byte-identical** — 82.9%, range [57.5, 90.7]. Both seams contribute exactly 0 pp: the
within-partner fraction is keyed on the sequenced exon pair, and neither `e13::e2` nor `e6::e2` is in
the cohort's measured distribution. Their value is that both identity-clean patient-derived EMC lines
become testable under *either* reading of an ambiguous vendor exon call.
