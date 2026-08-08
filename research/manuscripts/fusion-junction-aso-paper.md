---
id: DOC-FUSION-JUNCTION-ASO-PAPER
title: "A fusion-selective antisense oligonucleotide against the EWSR1::NR4A3 breakpoint junction: RNA-level fusion-exclusivity"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `manuscript` from its location under research/manuscripts/.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# A fusion-selective antisense oligonucleotide against the EWSR1::NR4A3 breakpoint junction: RNA-level fusion-exclusivity that the NR4A3 degrader cannot reach

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
> [`fusion-neoantigen-retraction.json`](../modalities/fusion-neoantigen-retraction.json) grades
> **`SEAM_NOT_PRODUCED`**, against a corrected
> `nr4a3_resume_range_across_plausible_breakpoints` of **[1, 1]** in
> [`fusion-object-inventory.json`](../modalities/fusion-object-inventory.json). So those panels
> describe a chimera missing NR4A3 residues 1–360 — AF1 and the first zinc finger of the C4 DBD,
> which opens at C292 — that no plausible breakpoint in the declared windows produces.
> Primary record: [`systems/AUDIT-2026-08-06-routes.md`](../../systems/AUDIT-2026-08-06-routes.md)
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
> ([`nr4a3-exon-audit.json`](../modalities/nr4a3-exon-audit.json)): e7 793, e9 1012, e10 1045,
> e12 1294, e13 1417 are all ≡ 1 — and **e11 1164 ≡ 0**. The set of junctions the pipeline emitted
> ({7, 9, 10, 12, 13}) and the single one it refused ({11}) are **exactly** what the off-by-two
> predicts. The "integrity flag" was the defect announcing itself, and it was read as an exon-boundary
> uncertainty for a month.
>
> **⛔ Three panels this manuscript cites have never existed.** §3a-quinquies claims a "full
> recurrent-junction panel (now run, real, committed — 2026-07-03)" over
> `junction-aso-offtarget-e{9,10,13}n3.json` and `junction-sirna-designs-e{7,9,10,12,13}n3.json`.
> Searched 2026-08-06: **none of those filenames is present on `origin/main`, on
> `origin/modalities-cache`, or in any commit reachable from this clone's refs.** Only the E7::N3
> and E12::N3 files exist, and those six are the ones carrying `_RETRACTED_SEAM` banners. Every
> quantitative statement sourced to E9/E10/E13 — the siRNA GC ranges, "a fully-clean 16-mer gapmer
> appears at 1 of 5 junctions", and the gapmer+siRNA panel-coverage conclusion — therefore rests on
> files nobody can read. They are withdrawn as unverifiable, independently of the seam defect.
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
> repo. That was true of [`nr4a3-exon-audit.json`](../modalities/nr4a3-exon-audit.json), which
> records coding nt per exon only, and **false of the repo**:
> [`emc-construct-inputs.json`](../modalities/emc-construct-inputs.json) carries the spliced cDNA,
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
> resolution: [`fusion-object-inventory.json`](../modalities/fusion-object-inventory.json) →
> `gate._phase_note_resolution`.
>
> **(d) And it inverts the E11::N3 arithmetic, which is the sharpest check available that the
> correction is the right one.** Under the *defective* index the chimeric CDS was in frame exactly
> when the EWSR1 cut ≡ 1 (mod 3) — admitting e7/e9/e10/e12/e13 and refusing **e11**. Under the
> corrected mRNA-level model the condition is (cut + 2) ≡ 0 (mod 3) — which admits **e7 and e12,
> the two junctions this manuscript leads with**, and now refuses **e11**. Both models refuse e11
> and for different arithmetic; the corrected one restores exactly the junctions the defective one
> was accidentally admitting. Every declared exon pair is graded in
> [`junction-mrna-frame-audit.json`](../modalities/junction-mrna-frame-audit.json) — the table this
> lane never had, which designs nothing and refuses out loud.
>
> **(e) Two independent reads agree, and this time they can fail independently.** The BLAST screen
> ran on a GitHub-hosted CPU runner from a **live Ensembl read** (2026-08-06); the audit, the design
> panels and the artifact headers were rebuilt offline from the **2026-08-03 committed cache**. The
> two produce **byte-identical designs and an identical measured junction**. That is the check the
> retracted panels never had: E7::N3 and E12::N3 agreeing was one defect producing both, whereas
> these are two separate acquisitions of the transcript model.
>
> **(f) STILL WITHDRAWN, unchanged.** The E9/E10/E13 panels and the `junction-sirna-designs-e*n3`
> files **do not exist** and were never regenerated, because there was nothing to regenerate. Every
> statement sourced to them — the siRNA GC ranges, *"a fully-clean 16-mer gapmer appears at 1 of 5
> junctions"*, and the gapmer+siRNA panel-coverage conclusion — remains withdrawn as unverifiable.
> **The corrected panel covers 2 junctions, not 5.**
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

> **In-silico design / feasibility draft (2026-06).** No wet lab; no molecule synthesized; **no new
> GPU run was performed** — the real results cited here are CPU outputs: the committed gapmer designs
> [`../modalities/junction-aso-designs.json`](../modalities/junction-aso-designs.json) (5 fusion-specific
> gapmers), a transcriptome-wide off-target screen
> [`../modalities/junction-aso-offtarget.json`](../modalities/junction-aso-offtarget.json) (0 of 5 free of
> gap-spanning near-matches), and a junction-siRNA design set
> [`../modalities/junction-sirna-designs.json`](../modalities/junction-sirna-designs.json) (0 of 5 pass;
> min GC 73.7%), a full-transcriptome (uncapped, 186,185-transcript) off-target + accessibility + siRNA-seed
> evaluation [`../modalities/aso-insilico-evaluation.json`](../modalities/aso-insilico-evaluation.json) (0 of 5
> canonical gapmers off-target-free; true ≤1-mismatch counts 8–95, not the capped "50"), a per-breakpoint
> feasibility scan
> [`../modalities/junction-breakpoint-scan.json`](../modalities/junction-breakpoint-scan.json) (390 modelled
> breakpoints; 243, or 62%, favorable; the canonical one is not), and a gap-mismatch-resolved off-target
> screen on a favorable breakpoint
> [`../modalities/junction-aso-offtarget-bp200-8-gapres.json`](../modalities/junction-aso-offtarget-bp200-8-gapres.json),
> re-scored under a graded fold-discrimination model
> [`../modalities/junction-aso-offtarget-bp200-8-gapres-graded.json`](../modalities/junction-aso-offtarget-bp200-8-gapres-graded.json)
> (**0 of 5 gapmers predicted off-target-clean**; the designs separate by predicted cleavage load over more
> than an order of magnitude, and it is that separation — not a clean call — that the screen supports.
> ⚠ *Superseded, retained: "2 of 5 gapmers predicted clean — zero true RNase-H cleavage risk", which counted
> every gap-disrupted near-match as zero-cleavable; see §3a-quater and Appendix A, entry 68*), corroborated
> by an uncapped full-transcriptome screen on the same favorable breakpoint
> [`../modalities/aso-insilico-evaluation-bp200-8.json`](../modalities/aso-insilico-evaluation-bp200-8.json)
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
([`junction-aso-designs.json`](../modalities/junction-aso-designs.json)), each drawing bases from both
sides of the seam and absent as a perfect complement from either parent CDS — together with the honest
caveat that surfaces immediately: this junction is **GC-rich (~75–81% GC)**, outside the usual comfort
zone, and would need chemistry tuning. Two further real, committed CPU results sharpen this caveat: a
transcriptome-wide off-target screen (blastn-short vs human RefSeq RNA) finds **0 of 5** gapmers free of
gap-spanning (RNase-H-cleavable) near-matches, and a GC-tolerant junction siRNA route does **not** rescue
the chemistry — its lowest-GC fusion-specific guide is still **73.7% GC**, so **0 of 5** siRNA guides pass
all filters. The honest synthesis is that this *modelled* breakpoint sequence is intrinsically GC-rich and
low-complexity, hurting gapmer chemistry, siRNA GC, and predicted specificity at once — a property of this
junction, not of the modality. A new per-breakpoint feasibility scan
([`junction-breakpoint-scan.json`](../modalities/junction-breakpoint-scan.json)) confirms this directly:
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
on each patient's sequenced breakpoint. We then specify what else is computable *now* without any GPU (extended
tiling and a breakpoint-keyed per-patient panel), and we are explicit that the genuinely unsolved problem is **tumour delivery**, which
we discuss only at the hypothesis level (e.g. a B7-H3-targeted antibody–oligonucleotide conjugate or a
receptor-targeted nanoparticle). We ask others to run one decisive experiment: junction-ASO versus
scrambled-control knockdown in patient-derived EMC lines (USZ-EMC [Bangerter]; NCC-EMC [Iwata]), with
specificity confirmed by sparing of the parental transcripts. The platform generalises to any
recurrent-fusion cancer with a defined breakpoint; EMC is the proof-of-concept entry indication.

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
to remove the protein (see [`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)). That LBD is retained
near-intact in the fusion, and its amino-acid sequence is **identical** to that of wild-type NR4A3. A
ligand that binds the fusion's LBD therefore cannot, in principle, distinguish the fusion from wild-type
NR4A3: the degrader is **NR4A3-selective but not fusion-selective**. The degrader paper handles this
honestly — its selectivity work is *paralogue* selectivity (NR4A3 vs NR4A1/NR4A2), not *fusion-vs-wildtype*
selectivity — and it is bounded by NR4A3's own tumour-suppressor roles (combined NR4A1/NR4A3 loss causes
AML [Mullican]; NR4A3 is tumour-suppressive in HCC/breast/lymphoma [Safe & Karki]). Removing wild-type
NR4A3 systemically is thus a real liability the degrader must manage.

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

**(v) ⛔ A junction-targeted agent has been taken into clinical testing.** **PMID 27166877** — a bi-shRNA
against *"the identical type 1 translocation junction region of the EWS/FLI1 transcribed mRNA"*, reporting
85–92 % target knockdown and stating that the results *"provide the justification to initiate clinical
testing"*; follow-through in patients is **PMID 36780200**. A reviewer knows this. The manuscript must not
read as though it does not.

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
count of junction-directed oligonucleotide work against EWSR1::NR4A3 — or against *any* NR4A3 fusion — is
**zero**. Against **108** junction-plus-oligo records for BCR::ABL1 and **37** for EWSR1::FLI1, EMC is not a
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

[`research/modalities/junction_aso.py`](../modalities/junction_aso.py) fetches the RefSeq CDS of *EWSR1*
(NM_005243) and *NR4A3* (NM_006981) from NCBI, builds the **modelled** fusion CDS at the canonical
protein-level breakpoint (EWSR1 kept to codon 264; NR4A3 retained from codon 2 — flagged in the output as
an assumption), and tiles 16-mer 5-6-5 gapmers whose central DNA gap spans the junction. It keeps only
oligos that (i) draw bases from **both** sides of the seam and (ii) are **not** a perfect complement of
either parent CDS. The committed result
([`junction-aso-designs.json`](../modalities/junction-aso-designs.json)) reports **5 fusion-specific
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
> → NR4A3 exon 3; [`novel-modalities.md`](./novel-modalities.md) §3.3), whereas "NR4A3 from codon 2" retains
> almost the entire NR4A3 CDS — so the *modelled* junction seam is not the seam of the commonly reported
> EWSR1 exon-7/12 :: NR4A3 exon-3 fusion ([citation to verify] for the rank-order of recurrent exon
> junctions).
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
([`junction-aso-offtarget.json`](../modalities/junction-aso-offtarget.json)).**
[`junction_aso_offtarget.py`](../modalities/junction_aso_offtarget.py) BLASTs each gapmer (blastn-short,
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
([`junction-sirna-designs.json`](../modalities/junction-sirna-designs.json)).**
[`junction_sirna.py`](../modalities/junction_sirna.py) designs junction-spanning 19-mer siRNA guides
(RISC/Ago2, GC window 30–52%) as the GC-tolerant fallback of §2b. It returns **5 fusion-specific guides,
but 0 pass all filters**, because the **minimum GC among the fusion-specific guides is 73.7%** — far above
the 30–52% target window. So the siRNA route **does not rescue** the GC problem at this breakpoint; the same
GC-rich seam that troubles the gapmer also disqualifies every siRNA guide.

**(iii) Full-transcriptome (uncapped) off-target + accessibility + siRNA-seed evaluation
([`aso-insilico-evaluation.json`](../modalities/aso-insilico-evaluation.json)).**
[`aso_insilico.py`](../modalities/aso_insilico.py) re-screens the same five canonical-breakpoint gapmers
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
[`novel-modalities.md`](./novel-modalities.md) §3.3 — ⛔ **that enumeration is retracted**; see §3b.4 and
[`fusion-neoantigen-retraction.json`](../modalities/fusion-neoantigen-retraction.json). Breakpoint
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
directly. [`junction_breakpoint_scan.py`](../modalities/junction_breakpoint_scan.py) sweeps a grid of
**390 modelled in-frame breakpoints** (EWSR1 kept-length 200–300 codons × NR4A3 start 2–30 codons) and
triages each junction by junction-window GC (±10 nt), ±12 nt Shannon entropy, low-complexity repeat, and
whether a *fusion-specific* gapmer or siRNA exists with GC in the 40–60% comfort band. The committed result
([`junction-breakpoint-scan.json`](../modalities/junction-breakpoint-scan.json)) **largely resolves the
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
   [`novel-modalities.md`](./novel-modalities.md) §3.3 — enumeration retracted, §3b.4) is bracketed in codon
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
liability ([`junction-aso-offtarget-bp200-8-gapres.json`](../modalities/junction-aso-offtarget-bp200-8-gapres.json)).
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
  ([`junction-aso-offtarget-bp200-8-gapres-graded.json`](../modalities/junction-aso-offtarget-bp200-8-gapres-graded.json),
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
  breakpoint* ([`aso-insilico-evaluation-bp200-8.json`](../modalities/aso-insilico-evaluation-bp200-8.json)).
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
> [`fusion-neoantigen-retraction.json`](../modalities/fusion-neoantigen-retraction.json) grades
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
> [`aso-offtarget.yml`](../../.github/workflows/aso-offtarget.yml) `real_junctions: "12:3 7:3"`,
> which is the only route in this repository that runs them.

The red-team's lead open gap was that every screen above ran on *modelled* breakpoints, never on the
**actually recurrent** EWSR1::NR4A3 exon junctions. That gap is now closed. We built the real fusion CDS
directly from Ensembl MANE/canonical exon structure (reusing the companion `fusion_breakpoints.gene_model`;
self-checked `translate(CDS) == Ensembl protein`, NR4A3 C-terminus intact) and ran the **full** pipeline —
design → gap-resolved BLAST → uncapped full-transcriptome eval — on the two most commonly reported junctions,
**EWSR1 exon-12 :: NR4A3 exon-3** (the most common) and **EWSR1 exon-7 :: NR4A3 exon-3**
([`junction-aso-designs-e12n3.json`](../modalities/junction-aso-designs-e12n3.json),
[`junction-aso-offtarget-e12n3.json`](../modalities/junction-aso-offtarget-e12n3.json),
[`aso-insilico-evaluation-e12n3.json`](../modalities/aso-insilico-evaluation-e12n3.json), and the `-e7n3`
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
> [`junction-aso-offtarget-e7n3-graded.json`](../modalities/junction-aso-offtarget-e7n3-graded.json) and
> [`junction-aso-offtarget-e12n3-graded.json`](../modalities/junction-aso-offtarget-e12n3-graded.json);
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
  > ([`nr4a3-exon-audit.json`](../modalities/nr4a3-exon-audit.json)): e7 793 ≡ 1, e9 1012 ≡ 1,
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
> three of the five junctions' files do not exist. ⚠ **The comparison it draws is the most
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
[`junction-mrna-frame-audit.json`](../modalities/junction-mrna-frame-audit.json); a panel is emitted only for a
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

Sources: [`junction-aso-designs-e7n3.json`](../modalities/junction-aso-designs-e7n3.json),
[`junction-aso-offtarget-e7n3.json`](../modalities/junction-aso-offtarget-e7n3.json),
[`aso-insilico-evaluation-e7n3.json`](../modalities/aso-insilico-evaluation-e7n3.json) and the `-e12n3`
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

### 3b. What is specifiable now, without any GPU

All of the following are CPU-only and need no new GPU/compute run; they are specified, not executed, in
this draft:

1. **Expanded tiling, with a gap-centred specificity rule — gap-level margin now DONE; longer-oligo tiling
   still specifiable.** The §2a fix is **implemented**: `junction_aso.py` now computes a
   **`gap_specificity_margin`** (junction-unique bases *inside* the 6-nt catalytic gap on the shorter side) and
   a `gap_centered` flag, and ranks by it — the operative discriminator, retiring the overstating oligo-wide
   `specificity_margin` (committed in every real-junction design JSON). What remains specifiable (not yet run)
   is the **wider-window, multi-length tiling** (14–20-mers, both 5-6-5 and 5-10-5), which the panel above
   (§3a-quinquies) motivates directly: since clean 16-mer gapmers are the exception, a 5-10-5 20-mer sweep is
   the most promising lever to convert the 1–3-residual-risk junctions (E9/E10/E12) into clean designs.
2. **Genome-wide off-target complementarity screen (CPU) — DONE for the modelled breakpoint (§3a-bis i).**
   The current design-time check only confirms an oligo is not a *perfect* complement of the two parent
   CDSs; a real specificity claim requires a transcriptome-wide near-match search with gap-region weighting
   (RNase-H tolerates wing mismatches more than gap mismatches). **This has now been run** (blastn-short vs
   The current design-time check only confirms an oligo is not a *perfect* complement of the two parent
   CDSs; a real specificity claim requires a transcriptome-wide near-match search with gap-region weighting
   (RNase-H tolerates wing mismatches more than gap mismatches). **This has now been run** on the modelled
   reference junction (poor — §3a-bis), the favorable modelled 200/8 junction (§3a-quater), **and — closing
   the red-team's lead gap — on the real recurrent EWSR1 exon-12/exon-7 :: NR4A3 exon-3 junctions
   (§3a-quinquies)**, built exon-exact from Ensembl structure via the companion `fusion_breakpoints.py`. The
   real junctions are markedly more GC-favorable than the modelled reference and yield a predicted-clean
   gapmer at E7::N3; the remaining specifiable items are now the gap-centred re-tiling (§3b.1) and screening
   any *additional* in-frame patient breakpoints as they are sequenced.

   **Per-breakpoint feasibility scan — DONE (§3a-ter), and the favorable-breakpoint screens are now DONE too
   (§3a-quater).** The sensitivity sweep over 390 modelled breakpoints has been run and committed
   ([`junction-breakpoint-scan.json`](../modalities/junction-breakpoint-scan.json)); the reference position is
   unfavorable and in-band designs exist elsewhere. Both the gap-resolved BLAST screen and the uncapped
   full-transcriptome screen have since been run on the favorable 200/8 example (§3a-quater) — so the
   remaining specifiable items are the **real exon-3 junction** designs (above) and the gap-centred re-tiling,
   not "run a screen on a favorable breakpoint."
3. **siRNA alternative (computable) — DONE for the modelled breakpoint (§3a-bis ii).** Junction-spanning
   19-mer siRNA guides have now been generated (asymmetry/end-stability/run filters); at this breakpoint 0
   of 5 pass (min GC 73.7%), so the GC-tolerant route does not rescue this junction. Seed off-target
   counting against the transcriptome remains specifiable for any breakpoint that yields in-window-GC guides.
4. **Breakpoint heterogeneity → a per-patient panel.** ⛔ *The "7 distinct in-frame junctions" citation
   below is RETRACTED at source:* [`fusion-neoantigen-retraction.json`](../modalities/fusion-neoantigen-retraction.json)
   grades all seven — six `SEAM_NOT_PRODUCED`, one `SEAM_RELABELLED`, **zero with a reproduced NR4A3
   label**. ⚠ **The paragraph's own conclusion is unaffected and is *strengthened*, which is why it is
   kept:** designs are breakpoint-conditional and the deliverable is a panel keyed to a *sequenced*
   breakpoint. That was true when the exon enumeration was thought sound and is more obviously true now
   that it is not. What is withdrawn is the specific enumeration, not the argument it was used to
   illustrate. *Superseded, retained:* Because EMC breakpoints vary by exon usage (the
   companion neoantigen work resolved *7 distinct in-frame junctions* across EWSR1 exons 7/9/10/11/12/13 →
   predominantly NR4A3 exon 3; see [`novel-modalities.md`](./novel-modalities.md) §3.3), the ASO sequence
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
So we ran an unbiased scan — [`emc_surfaceome_scan.py`](../modalities/emc_surfaceome_scan.py) →
[`emc-surfaceome-scan.json`](../modalities/emc-surfaceome-scan.json) — of the whole human surfaceome (UniProt
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
- **Honest bounds (stated in the JSON too).** It is a **surrogate** — DepMap *sarcoma* lines, not EMC (EMC has
  no DepMap line); the myxoid subset closest to EMC is a **single line** (anecdotal — the n=76 translocation
  class carries the signal); "enrichment" is vs other **cancer** lineages, **not normal tissue**, so the
  toxicity-relevant tumour-vs-normal window (GTEx/HPA) is the flagged next filter; and cell-line surface *mRNA*
  is a proxy for primary-tumour surface *protein*. This **names a candidate antigen; it does not confirm EMC
  surface expression** (that needs the EMC lines' own data — see below) and **does not solve delivery
  efficiency** (blood→tumour→cell→endosomal escape stays wet-lab).

**The decisive upgrade — real EMC data (now probed, real, committed — 2026-07-03).** EMC is no longer
model-less: patient-derived **USZ-EMC** [Bangerter 2022/2023] and **NCC-EMC1-C1** [Iwata 2025] exist and are
being studied. A data probe ([`emc_line_data_probe.py`](../modalities/emc_line_data_probe.py) →
[`emc-line-data-probe.json`](../modalities/emc-line-data-probe.json); Europe PMC full-text + NCBI GEO/SRA)
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
  ([`emc_gse4303_crosscheck.py`](../modalities/emc_gse4303_crosscheck.py) → `emc-gse4303-crosscheck.json`)
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
> **target-class** manuscript, [`emc-surface-target-landscape.md`](./emc-surface-target-landscape.md)
> (scaffolded, gated on the real EMC surface data above) — the way the degrader paper was split from the EMC
> roadmap. This section keeps only the *delivery-arm* relevance to the ASO; the antigen landscape lives there.

No delivery claim is made; this section exists to mark delivery as the dominant risk, to **narrow the
targeting-arm unknown from "none named" to a data-ranked shortlist**, and to point at the EMC lines that could
confirm it — not to assert a solution.

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
- **Spares wild-type NR4A3 — and therefore avoids the tumour-suppressor liability the degrader carries.**
  This is the key safety advantage over the LBD degrader. Because the junction is absent from wild-type
  *NR4A3*, the oligo does not touch the wild-type transcript, side-stepping the AML risk of combined
  NR4A1/NR4A3 loss [Mullican] and the HCC/breast/lymphoma tumour-suppressor roles of NR4A3 [Safe & Karki].
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
  screen, §3a-ter/§3a-quater). ⛔ **Caveat (iii) — that the screens had only run on modelled positions —
  is OPEN, not addressed.** *Superseded, retained: "has now been **addressed**: the full pipeline was
  run on the real EWSR1 exon-12/exon-7 :: NR4A3 exon-3 junctions (§3a-quinquies), which are more
  GC-favorable than the modelled grid and yield a predicted-clean gapmer at E7::N3 (E12::N3 needs
  per-oligo selection)."* Those runs used a seam graded `SEAM_NOT_PRODUCED`, so **every screen in this
  manuscript has still only run on modelled positions.** Every clinical design must still be
  re-derived from the patient's *sequenced* fusion transcript.
- **Delivery unsolved.** No validated tumour-delivery route for EMC exists; §3c lists hypotheses only. This
  is the dominant risk for the whole modality.
- **Knockdown, not knockout.** ASO/siRNA reduce transcript; they do not eliminate the gene or guarantee
  durable, complete loss of fusion protein. Depth and duration of knockdown are empirical.
- **⛔ THE PAPER NO LONGER CALLS ANY DESIGN "PREDICTED CLEAN", AND THE HEURISTIC THAT ALLOWED IT WAS NOT
  CONSERVATIVE.** The favorable-breakpoint calls assumed any mismatch inside the 6-nt gap abolishes RNase-H
  cleavage. **PMID 23963702** measures ~5-fold discrimination for an unmodified RNase-H-active ASO (>100-fold
  only with chemistry these designs lack), and **PMID 7567450** reports that 16mers — the length used here —
  "did not discriminate efficiently"; so the assumption was *optimistic*, not conservative, and against the
  length-matched source it fails outright. §3a-quater now reports a **residual predicted cleavage load** under
  both bounds, on which **0 of 5** designs reach zero. What the screens support is a **rank ordering** of
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

The junction-ASO concept is a **platform**, not an EMC-only tactic: it applies to **any recurrent-fusion
cancer with a defined, sequenced breakpoint**, because the only requirement is a tumour-specific mRNA seam
absent from both parent transcripts. Natural extensions include other **FET-family / EWSR1-fusion
sarcomas** (the EWSR1-rearranged sarcoma spectrum more broadly), where the same design-and-screen pipeline
([`junction_aso.py`](../modalities/junction_aso.py) plus the §3b CPU off-target screen) applies with only
the breakpoint sequence changed. EMC is the proof-of-concept entry indication precisely because it is the
cleanest case — a quiet genome with a single near-clonal fusion driver — so a positive parental-sparing
knockdown result here is the strongest possible demonstration that the platform discriminates fusion from
wild-type at the RNA level. *(Specific partner cancers beyond the EWSR1/FET family are not enumerated here
to avoid over-claiming; each would need its own breakpoint sourcing — [citation to verify] per indication.)*

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
on-demand: [`scripts/method-watch.mjs`](../../scripts/method-watch.mjs),
[`.github/workflows/method-watch.yml`](../../.github/workflows/method-watch.yml); digest published to the
`method-watch-cache` branch). The capability → action trigger table lives in
[`research/method-watch.md`](../method-watch.md); the rows specific to this paper are:

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
> [`lint_citations.py`](./lint_citations.py) anchors this prose against. The assessment of what the
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
  [`fusion-object-inventory.json`](../modalities/fusion-object-inventory.json)
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
  [`junction_aso_offtarget.grade_panel`](../modalities/junction_aso_offtarget.py) into
  [`junction-aso-offtarget-bp200-8-gapres-graded.json`](../modalities/junction-aso-offtarget-bp200-8-gapres-graded.json).
  **The new figure is 0 of 5 under both bounds** (§3a-quater; Appendix A, entry 68). The same regrade was run
  on the real-junction panels
  ([`-e7n3-graded.json`](../modalities/junction-aso-offtarget-e7n3-graded.json),
  [`-e12n3-graded.json`](../modalities/junction-aso-offtarget-e12n3-graded.json)) and changes no headline
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

⚠ **This manuscript has no related-work section, and the modality it proposes has a 35-year, continuous,
clinically-tested precedent.** The full assessment — including which of this paper's claims survive it — is
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
- **Clinical stage.** **PMID: 27166877 · PMC5023384 · doi:10.1038/mt.2016.93** — bi-shRNA EWS/FLI1 lipoplex,
  which *"targets the identical type 1 translocation junction region of the EWS/FLI1 transcribed mRNA"*, taken
  through IND-enabling work; follow-through in patients at **PMID: 36780200 · PMC10150239**. Review, 2026:
  **PMID: 42110475 · PMC13156592 · doi:10.1016/j.omton.2026.201213**.
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

- [`junction-aso-designs.json`](../modalities/junction-aso-designs.json) — 5 junction-spanning 5-6-5 gapmer
  designs, from [`junction_aso.py`](../modalities/junction_aso.py).
- [`junction-aso-offtarget.json`](../modalities/junction-aso-offtarget.json) — NCBI BLAST API (blastn-short
  vs RefSeq RNA) gap-spanning off-target screen of the canonical designs, from
  [`junction_aso_offtarget.py`](../modalities/junction_aso_offtarget.py) (HITLIST-capped at 50; over-calls).
- [`aso-insilico-evaluation.json`](../modalities/aso-insilico-evaluation.json) — **uncapped** full-RefSeq
  (186,185-transcript) off-target screen + ViennaRNA accessibility + siRNA-seed module of the canonical
  designs, from [`aso_insilico.py`](../modalities/aso_insilico.py).
- [`junction-sirna-designs.json`](../modalities/junction-sirna-designs.json) — junction siRNA route, from
  [`junction_sirna.py`](../modalities/junction_sirna.py).
- [`junction-breakpoint-scan.json`](../modalities/junction-breakpoint-scan.json) — 390-breakpoint GC/
  complexity/parent-specificity triage sweep, from
  [`junction_breakpoint_scan.py`](../modalities/junction_breakpoint_scan.py).
- [`junction-aso-offtarget-bp200-8.json`](../modalities/junction-aso-offtarget-bp200-8.json) and its
  gap-mismatch-resolved companion
  [`junction-aso-offtarget-bp200-8-gapres.json`](../modalities/junction-aso-offtarget-bp200-8-gapres.json) —
  the BLAST off-target screen re-run on the favorable EWSR1-keep-200 / NR4A3-from-8 breakpoint, resolved to
  true RNase-H cleavage risk, from [`junction_aso_offtarget.py`](../modalities/junction_aso_offtarget.py).
- [`aso-insilico-evaluation-bp200-8.json`](../modalities/aso-insilico-evaluation-bp200-8.json) — the
  **uncapped** full-RefSeq off-target + accessibility + siRNA-seed evaluation re-run on the same favorable
  breakpoint (4 of 5 gapmers with zero ≤1-mismatch off-targets), from
  [`aso_insilico.py`](../modalities/aso_insilico.py) (breakpoint-parameterised via env).
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
  is unchanged — **six files, two junctions** — and the `e9n3`/`e10n3`/`e13n3` and siRNA variants are
  still absent, so the withdrawal of every claim sourced to them stands exactly as written below.
  A citation to a file that does not exist cannot be checked by a reader and must not appear in a
  manuscript; these are withdrawn as unverifiable **independently of** the seam defect, which
  separately retracts the two panels that do exist. The e11:3 no-output is root-caused in
  §3a-quinquies and is not an exon-boundary uncertainty.
  ⚠ *One thing here was never in doubt and is not withdrawn:* the `gap_specificity_margin`
  gap-level discriminator (§2a/§3b.1) is a property of `junction_aso.design()` and is independent of
  which seam it is given.
- **EMC surfaceome scan (§3c):** [`emc-surfaceome-scan.json`](../modalities/emc-surfaceome-scan.json) (+ `.png`)
  from [`emc_surfaceome_scan.py`](../modalities/emc_surfaceome_scan.py) — unbiased UniProt surfaceome (2,820
  genes) ranked by expression across the EMC-surrogate translocation-sarcoma DepMap class; names a data-ranked
  delivery/CAR/ADC targeting-antigen shortlist (surrogate, not EMC; myxoid n=1; rest≠normal tissue).

No GPU computation was performed for this draft (the RNase-H1 cleavage-discrimination MD of §8 is the one
planned GPU experiment; all results above are CPU, via GitHub Actions → `modalities-cache`).
