# The EMC arm, pre-built — a collaborator package for the FET / ATM / ATR laser-microirradiation assay

**What this is:** everything a group that already runs the FET-fusion DSB-recruitment assay would
otherwise have to derive, decide or build in order to add **extraskeletal myxoid chondrosarcoma
(EMC)** as the untested fourth transcription-factor-partner class. Constructs, controls,
predictions and kill criteria, all fixed in advance.

**What it is not:** a request to be convinced by an argument. The argument for EMC is already
written down ([`emc-post-degrader-options.md`](./emc-post-degrader-options.md) route 1) and adding
more of it would add nothing. **This document exists to remove work and risk from their side, not
to add rhetoric to ours.**

> ## ⛔ Read this before anything else
>
> **Every construct below is a COMPUTED DESIGN FOR SOMEONE ELSE TO VERIFY BEFORE ORDERING.**
> Nothing here has been synthesised, expressed, sequenced or tested by anyone. No efficacy,
> safety, therapeutic-window or clinical claim is made or implied, anywhere, about anything.
>
> **And this repository has been wrong about a fusion junction before.** A committed artifact,
> built from a stated Ensembl methodology, indexed a *coding*-exon offset table with *transcript*
> exon numbers. The label "NR4A3 exon 3" resolved to transcript exon 5, and all seven junctions it
> emitted silently deleted NR4A3's AF-1 domain and the first zinc finger of its C4 DNA-binding
> domain — modelling a chimera that could not do the one thing the real fusion is reported to do.
> It survived review and was caught only by a free re-derivation
> ([`target-route-options.md` §1.3](./target-route-options.md)). That incident is why every
> boundary below carries its provenance and every construct carries a self-check, and it is why
> the honest framing of this package is *"here is our arithmetic, please check it"* rather than
> *"here are your reagents"*.

**Machine-readable companion, and the home of every number here:**
[`emc_fet_construct_designs.py`](../modalities/emc_fet_construct_designs.py) →
`emc-fet-construct-designs.json` (published to the `modalities-cache` branch and to this branch by
[`depmap-dependency.yml`](../../.github/workflows/depmap-dependency.yml)). Run
`python3 research/modalities/emc_fet_construct_designs.py --check` to reproduce it offline from
its inputs cache.

---

## 1 · The assay this serves, quoted rather than paraphrased

From the methods of the source paper (PMID 37205599 / bioRxiv 10.1101/2023.04.30.538578, fetched
to the `literature-cache` branch):

> *"U2OS cells expressing EWSR1-GFP, EWSR1-FLI1-GFP, EWSR1-ATF1-GFP, EWSR1-WT1-GFP or the various
> mutant forms of the fusion oncoproteins were seeded in 8-well Lab Tek II Chamber Slides … Cells
> were treated with 1µg/ml Hoechst 33342 … for 30 minutes prior to micro-irradiation … 5-pixel
> wide stripes were drawn in every cell nucleus … and irradiated with a 405nm diode laser (40mW).
> Images were acquired pre-irradiation and at 1-minute intervals post-laser damage for 15 minutes."*

So the unit of work is **a GFP-tagged ORF**. Adding EMC to that panel is not a new assay, a new
instrument or a new analysis — it is **new plasmids**. Which is exactly the part this package
supplies.

⚠ **Tag orientation is theirs to choose, and we deliberately do not choose it.** The source is
internally inconsistent — its methods write `EWSR1-FLI1-GFP` (C-terminal) while the Fig. 5 legend
writes `GFP-EWSR1-FLI1` (N-terminal). A tag can itself perturb an intrinsically-disordered region,
so the EMC constructs should be built in **whichever orientation their existing EWSR1-FLI1
construct uses**. The artifact therefore emits the **untagged ORF**.

---

## 2 · Deliverable 1 — the constructs

### 2.1 How the junction is computed, and why it is not done the obvious way

A reported fusion is an **mRNA exon junction**, not a protein junction. The constructs are
therefore built at the **cDNA** level — 5′ partner cDNA from its transcript start through the end
of the named exon, joined to 3′ partner cDNA from the start of its named exon — and then
translated **from the 5′ partner's own start codon**.

That distinction is not pedantry here. **NR4A3's transcript exons 1 and 2 are entirely non-coding,
and exon 3 carries both 5′-UTR and the start codon** ([`nr4a3-exon-audit.json`](../modalities/nr4a3-exon-audit.json)).
A CDS-level splice would silently discard that UTR; a transcript-level splice translates it in the
5′ partner's frame, which is the only way to find out whether the reported junction is in frame at
all. Every construct therefore carries three self-checks a reader can audit:

| self-check | what it asserts |
|---|---|
| `five_prime_start_matches_partner` | the ORF opens with the 5′ partner's own N-terminus |
| `three_prime_c_terminus_intact` | the ORF ends with the 3′ partner's own C-terminus |
| `in_frame` | both of the above |

**A construct that fails them is reported as failing and its sequence is withheld.** It is not
quietly dropped, and the breakpoint is not adjusted until it passes — "tune the input until the
answer is nice" is the exact circularity the positive controls in
[`emc_fet_idr_census.py`](../modalities/emc_fet_idr_census.py) were built to prevent.

### 2.2 ⚠ A correction this work forced, stated up front

**The junction this repo has been calling "the canonical EMC fusion" mixes two reported types.**
Route 1 and the IDR census both describe EMC's canonical junction as **EWSR1 exon 7 :: NR4A3 exon
3**, giving `EWSR1(1–264)`. The primary literature does not report that combination. It reports:

- **type 1, the commonest:** *"exon 12 of EWSR1 fused to exon 3 of NR4A3"*
- **type 2:** *"exon 7 of EWSR1 is fused to exon 2 of NR4A3"*

both quoted verbatim from PMC3335514, and both independently corroborated by Agaram 2014's RT-PCR
primer design (PMC4015728: an *EWSR1 exon 12* forward primer paired with an *NR4A3 exon 3* reverse
for type 1; an *EWSR1 exon 7* forward paired with an *NR4A3 exon 2* reverse for type 2), by
PMC4055444, and by a counted series (PMC2395470: 10 of 15 *EWS/CHN* tumours were exon 12 :: exon 3).

**This matters, and it makes the EMC case stronger rather than weaker** — see §3. The superseded
framing is registered in the appendix. **What it does *not* disturb** is the §1.3 finding: both
reported types retain NR4A3 from its own first coding exon, so NR4A3's AF-1, its C4 zinc finger and
its LBD are present in the fusion under either type. The off-by-two correction stands.

### 2.3 The registry — every breakpoint is a quote, never a memory

| construct | junction (transcript exon numbering) | reported rank | sources |
|---|---|---|---|
| **EWSR1::NR4A3 type 1** | EWSR1 e12 :: NR4A3 e3 | **commonest** | PMC3335514 · PMC4055444 · PMC4015728 (primers) · PMC6766969 (an expressed construct: *"E-N, corresponding to EWSR1 (exons 1-12)-NR4A3 (exons 3-8)"*) |
| **EWSR1::NR4A3 type 2** | EWSR1 e7 :: NR4A3 e2 | second | PMC3335514 · PMC4015728 (primers) |
| **EWSR1::NR4A3 type 5** | EWSR1 e13 :: NR4A3 e3 | minority | PMC4055444 · PMC2395470 (2 of 15) |
| **TAF15::NR4A3** | TAF15 e6 :: NR4A3 e3 | the only reported coding junction | PMC3335514 (*"exon 6 of TAF15 is fused **exclusively** to exon 3 of NR4A3"*) · PMC4055444 (*"**always**"*) · PMC2395470 · PMC6766969 (an expressed construct: *"T-N\*, corresponding to the commonest TAF15 (exons 1-6)-NR4A3 (exons 3-8) fusion"*) |

**A registered variant that is deliberately NOT modelled.** PMC6766969 also reports a rarer
TAF15::NR4A3 isoform (`T-N`) that splices into a cryptic exon in NR4A3 intron 2, *"thus encoding 25
additional amino acids prior to the NR4A3 ATG"*. **We do not emit it, because the cryptic exon's
sequence is in no artifact this repo holds and building it would mean inventing 75 nucleotides.**
The same source reports `T-N` and `T-N*` were *"essentially indistinguishable"* for colony
formation. It is listed so a collaborator knows it exists.

### 2.4 The two fusions we could **not** pin, named rather than omitted

| fusion | why no construct | what can still be said |
|---|---|---|
| **FUS::NR4A3** | no exon-level breakpoint statement found in this repo's literature cache | the breakpoint-**independent** sweep already published in [`emc-fet-idr-census.json`](../modalities/emc-fet-idr-census.json) → `emc_TAF15_and_FUS_breakpoint_sweep` answers the question as a *function* of breakpoint |
| **TCF12::NR4A3** | reported only at **genomic** resolution — *"the breakpoint affects the region of intron 5"* (PMC4055444) — and TCF12 has several alternatively-spliced isoforms | the negative control in §4 **does not need the junction**: it is computed over *every possible* TCF12 breakpoint, which is stronger than a prediction resting on one assumed junction |

**Naming a gap is part of the deliverable.** Silence would read as "there is no such fusion".

### 2.5 The wild-type controls the assay design implies

The source's own controls define both ends of the recruitment axis: native GFP-EWSR1 recruits
rapidly, and *"Control experiments with the full-length FLI1 protein showed no accumulation at
laser-induced DSBs"*. An EMC arm needs the same anchors **for its own partner genes**, or a delayed
curve cannot be told from a badly-expressed construct.

| control | role | registered prediction |
|---|---|---|
| **GFP-EWSR1** (full length) | fast-recruitment anchor — **they already have this construct** | rapid recruitment, as published. If it does not reproduce, nothing else in the run is interpretable |
| **GFP-TAF15** (full length) | wild-type anchor for the TAF15::NR4A3 arm | rapid recruitment, like native EWSR1 — TAF15 carries its own C-terminal RGG region. ⚠ **Not previously reported in this assay**, so this is a prediction, not a reproduction |
| **GFP-NR4A3** (full length) | partner-alone control — the EMC analogue of their GFP-FLI1 control | **no accumulation.** ⛔ If NR4A3 alone *is* recruited, the EMC fusion's recruitment cannot be attributed to the FET half and the whole structural argument for EMC fails at this single control |
| **GFP-TCF12** (full length) | partner-alone anchor for the negative-control arm | no accumulation — TCF12 is not a FET protein (computed, §4) |

Full-length sequences for all four are in the artifact under `wild_type_controls`.

---

## 3 · Deliverable 2 — the quantitative prediction, against **their own** calibration curve

### 3.1 The curve is theirs; we only place EMC on it

The source did not merely observe that FET fusions lose the RGG repeats — it built a **dose
series** and measured it:

> *"To test how loss of these RGG domains impact DSB recruitment of EWSR1-FLI1, we reintroduced
> either 1 or all 3 RGG-rich domains (the entire EWSR1 C-terminus) into the fusion oncoprotein. In
> an RGG dose-dependent manner, the RGG containing versions of EWSR1-FLI1 displayed earlier DSB
> recruitment kinetics and higher levels of overall recruitment when compared to EWSR1-FLI1."*

and reproduced it in a second disease: *"reintroduction of either 1 or all 3 RGG-rich domains into
EWSR1-ATF1 resulted in earlier DSB recruitment kinetics and higher levels of overall recruitment in
an RGG dose-dependent manner."*

**That is a calibration curve they already own, in an assay they already run.** The only thing
missing is where EMC's fusions fall on it.

**The axis is retained RG dipeptides of the 5′ FET partner, as a fraction of that partner's
wild-type total.** It is **threshold-free** — an RG dipeptide is either inside the retained segment
or it is not — and it is deliberately *not* a count of "RGG domains": the source names 3 in EWSR1
while this repo's operational box-finder merges them into 2, and tuning the box definition until it
returns 3 would be fitting the instrument to the expected answer. The underlying RG count needs no
definition at all. Arithmetic imported from
[`emc_fet_idr_census.py`](../modalities/emc_fet_idr_census.py); the box count is context only.

### 3.2 Where EMC lands — and the reason this is the interesting result

Retained EWSR1 RG dipeptides, computed from the Ensembl exon audit and the census's RG rule:

| construct | EWSR1 retained | RG kept | status |
|---|---|---|---|
| **EWSR1-FLI1** (the study's reference fusion, 0 RGG) | 1–264 | **0 of 30** | **measured** — delayed kinetics vs native EWSR1 |
| **EWSR1::NR4A3 type 2** (EMC) | 1–264 | **0 of 30** | *predicted* |
| **EWSR1::ATF1 e8** (clear cell, **commonest type**) | 1–324 | **7 of 30** | **measured — and the mechanism was found present** |
| **EWSR1::ATF1 e10** (clear cell) | 1–348 | **8 of 30** | **measured** |
| **EWSR1::NR4A3 type 1** (EMC, **commonest**) | 1–431 | **8 of 30** | *predicted* |
| **EWSR1::NR4A3 type 5** (EMC, minority) | 1–472 | **11 of 30** | *predicted* |
| **EWSR1-RGG(3)-FLI1** / native EWSR1 (3 RGG) | full | **30 of 30** | **measured** — earliest, highest |

⭑ **EMC's two main fusion types bracket the two fusions in which the mechanism was actually
measured.** Type 2 sits exactly where EWSR1-FLI1 sits (0 of 30, and the census reports the retained
segment as byte-identical over the shared prefix). Type 1 sits exactly where the *commonest
reported clear-cell type* sits (8 vs 7 of 30). **Neither EMC type is an extrapolation off the end
of their calibration curve — both are interpolations between points they have already measured.**

⚠ **This is why §2.2's correction strengthens the case rather than weakening it.** Under the old,
mixed junction EMC had one row, at zero, and the honest reading was "EMC loses at least as much RGG
content as every measured fusion". Under the sourced junctions EMC has **two** rows straddling both
measured fusions — which is a more specific, more falsifiable, and more interesting claim.

⚠ **And it must not be misread as a bar.** The commonest clear-cell type **retains** RG dipeptides
and the mechanism was measured in that disease anyway. So *retaining some RG content is not a
prediction of no phenotype.* "Loses the C-terminal RGG repeats" means losing the bulk, not literally
all — which is exactly why the axis is a comparison and never a threshold.

### 3.3 The registered predictions

**Registered before any experiment, and dated by this file's commit rather than by a line of
prose.** One home for the machine-readable versions:
`emc-fet-construct-designs.json` → `rgg_dose_calibration_and_predictions.registered_predictions`.

| id | prediction | falsified by |
|---|---|---|
| **P1** | **EWSR1::NR4A3 type 2 is recruited to laser-induced DSBs with kinetics indistinguishable from EWSR1-FLI1.** Basis: 0 of 30 RG retained, the same zero as their reference construct, on a byte-identical EWSR1 segment | no accumulation at the stripe; or kinetics matching *native EWSR1* rather than the fusion reference |
| **P2** | **EWSR1::NR4A3 type 1 (the commonest EMC fusion) is recruited, EARLIER than type 2, and closest to the commonest clear-cell EWSR1::ATF1 type.** Basis: 8 of 30 vs 7 of 30 | type 1 recruiting no earlier than type 2 — which would say retained RG content is not the variable; or type 1 not being recruited at all |
| **P3** | **TAF15::NR4A3 is recruited, at or near the zero end of the axis.** Basis: the TAF15 exon-6 RG count from the exon audit built for this deliverable | kinetics indistinguishable from native TAF15 |
| **P4** ⭐ | **EMC supplies, in nature, the RGG dose series they had to ENGINEER.** Type 2 (0 RG) and type 1 (8 RG) are two naturally occurring points on the same axis, in the same disease, with the same 3′ partner. If the RGG dose-dependence is real, that pair must reproduce it **with no add-back construct at all** | the pair showing no kinetic difference — which would bound the RGG dose-dependence to engineered constructs |
| **P5** | **TCF12::NR4A3 is NOT recruited** — see §4, the arm that can actually falsify the hypothesis | recruitment of TCF12::NR4A3 |

### 3.4 ⛔ What is explicitly **not** predicted

- **Retained RGG content is one input to recruitment kinetics, not the only one.** The source's own
  data show a second variable — EWSR1::ATF1 recruits like EWSR1-FLI1 but with *"differences in
  departure timing"* — and recruitment depends *"at least in part"* on **native EWSR1**, which these
  constructs do not control.
- **No effect size.** The axis is **ordinal** — earlier/later, more/less — because the source
  reports it that way. A fabricated slope would be false precision.
- **Nothing downstream.** These predictions are about **recruitment kinetics only**. They say
  nothing about ATM suppression, ATR dependency, drug sensitivity, efficacy, safety, dosing, or any
  clinical question, and nothing may be read as if they did.
- **The 3′ partner is a nuclear receptor** with its own DNA-binding domain. The source showed a DBD
  mutation did not change EWSR1-FLI1's DSB localisation — reassuring, but measured on an ETS DBD,
  not a C4 zinc finger. That is a reason to run GFP-NR4A3 alone (§2.5), not a reason to assume.

---

## 4 · Deliverable 3 — the within-EMC negative control, which is the most informative arm

**≈3–4 % of EMC carries `TCF12::NR4A3`, and TCF12 is not a FET-family gene.** Our argument
therefore predicts that **these cases should not show the phenotype.** That is a prediction that can
be tested *inside* EMC, on the same slide, in the same session.

### 4.1 "TCF12 is not FET" is computed, not asserted

Three independent tests, one of them with its own positive control, all in
`emc-fet-construct-designs.json` → `tcf12_negative_control`:

1. **N-terminal [S,Y,G,Q] composition** — the FET prion-like signature — for TCF12 against all
   three FET proteins.
2. **RG dipeptide content**, whole-protein and N-terminal, and the operational RGG-box count.
3. **Sequence identity of the N-terminal window**, by a plain Needleman–Wunsch alignment, with the
   **FET-vs-FET pairs computed by the identical call as the positive control**. A single identity
   value in isolation is uninterpretable; the *contrast* is the measurement.
4. ⭐ **A breakpoint-independent sweep.** Because the TCF12 junction is reported only at genomic
   intron-5 resolution, the control must not rest on one assumed junction — so the test asks, over
   **every** TCF12 N-terminal prefix from 50 aa to full length, whether *any* of them reaches the
   compositional range the three FET N-termini occupy.

**Computed result:** see §7 for the measured values and the verdict as the artifact records it.

### 4.2 The prediction, and what a violation would mean

> **P5 — `TCF12::NR4A3` is not recruited to laser-induced DSBs.** It should behave like the
> source's own full-length FLI1 control, which *"showed no accumulation at laser-induced DSBs"*.

**Why this is the single most valuable arm in the package: every other arm can only confirm. This
one can falsify.**

| observed | what it means |
|---|---|
| TCF12::NR4A3 **not** recruited, EWSR1::NR4A3 recruited | the prediction holds, and the FET-specificity of the mechanism is demonstrated *within one disease* rather than across diseases — which no experiment in the source paper does |
| **TCF12::NR4A3 recruited AND EWSR1::NR4A3 recruited** | ⛔ recruitment is driven by something the two chimeras share that is **not** the FET IDR. The obvious candidate is the NR4A3 half — which is precisely why GFP-NR4A3 alone is a required control in the same run. **The class argument for EMC would be wrong, and so would the structural mechanism as stated** |
| TCF12::NR4A3 recruited, EWSR1::NR4A3 not | the structural argument is inverted and this repo's census is measuring the wrong feature |
| neither recruited | EMC does not inherit the lesion by this readout. A clean, publishable negative — **worth as much as a hit**, and it saves other groups the experiment |

⚠ **No TCF12::NR4A3 construct is emitted**, for the reason in §2.4. A collaborator holding a
TCF12::NR4A3 case should sequence the junction. Failing that, **the arm can be run with full-length
GFP-TCF12**, which tests the same thing this control exists for: whether a non-FET N-terminus
reaches a double-strand break at all.

---

## 5 · What this actually saves them

| task | without this package | with it |
|---|---|---|
| decide which EMC junction to build | read the EMC fusion-variant literature; discover the type-1/type-2 split; pick | four sourced junctions with counted frequencies, each with its quote |
| get the junction right | exon-numbering arithmetic across two transcripts, with a UTR-bearing first coding exon — the step this repo got wrong once | computed ORFs with three auditable in-frame self-checks, and sequences withheld where the checks fail |
| decide the controls | infer from their own paper which anchors an EMC arm needs | four named wild-type controls with registered predictions and full sequences |
| decide what counts as a result | — | five predictions registered before the experiment, with explicit falsifiers |
| get a falsifiable arm | — | a within-EMC negative control with a computed basis and a stated consequence for the whole hypothesis |
| the ATR-inhibitor half | — | already preregistered: [`emc-atri-prereg.md`](../modalities/emc-atri-prereg.md), including the PARP-inhibitor negative-translation control |

**Nothing in this package asks them to accept a claim. It asks them to check arithmetic they can
check in an afternoon, and then run four plasmids.**

---

## 6 · Limits, stated so this is read correctly

1. **These are computed designs, not validated reagents.** Nothing here has been synthesised,
   expressed or sequenced. Every junction must be verified against the collaborator's own
   sequenced breakpoint before anything is ordered.
2. **This repository has been wrong about a junction before**, in a committed artifact, from a
   stated methodology, and it survived review (§0, §2.2). Treat this the same way: as arithmetic
   to audit.
3. **Canonical Ensembl transcripts only.** A patient's tumour may use a different transcript or a
   different breakpoint; the exon→residue map, and therefore the protein, would change.
4. **The predictions concern DSB-recruitment kinetics and nothing else.**
   No claim is made about ATM signalling, ATR dependency, drug sensitivity, efficacy, safety, tolerability, dosing, patient selection, or clinical readiness — none of those is asserted, implied or testable by anything here.
5. **Retained RGG content is one input among several**, and the constructs do not control native
   EWSR1, which the source shows contributes.
6. **FUS::NR4A3 and TCF12::NR4A3 have no sourced transcript-level junction here.** That is a gap in
   our sourcing, not evidence about the fusions.
7. **Nobody has been contacted.** Outreach is an outward-facing act and is gated
   (CLAUDE.md §3); a held draft exists at
   [`emc-atri-outreach-DRAFT.md`](../modalities/emc-atri-outreach-DRAFT.md) and has not been sent.
8. **No wet-lab work is proposed by us.** This program has no laboratory. The entire deliverable is
   the design, the prediction and the criteria.

---

## 7 · Computed values, as the artifact records them

*(Filled from `emc-fet-construct-designs.json` after the CI run that produces it. Any figure in
this section that disagrees with the artifact is a bug in this file, not in the artifact — the
artifact is the home.)*

---

## Appendix — superseded, retained

- **"EMC's canonical fusion is EWSR1 exon 7 :: NR4A3 exon 3, i.e. `EWSR1(1–264)`."** Used by
  [`emc_fet_idr_census.py`](../modalities/emc_fet_idr_census.py) (`emc_canonical_EWSR1_NR4A3`),
  by [`emc-post-degrader-options.md`](./emc-post-degrader-options.md) route 1, and by
  [`target-route-options.md` §1.3](./target-route-options.md). **Superseded 2026-08-03**: the
  primary literature reports **EWSR1 e12 :: NR4A3 e3 (type 1, commonest)** and **EWSR1 e7 ::
  NR4A3 e2 (type 2)**; the combination "e7 :: e3" pairs the 5′ side of one with the 3′ side of the
  other and is not a reported type. The census row remains **valid arithmetic for a 264-residue
  EWSR1 cut** and remains the right comparator for EWSR1-FLI1 type 1 — what changes is the label
  "canonical", which now belongs to the exon-12 cut. Retained here because the old figure
  (`0 of 30 RG`) is quoted in live text elsewhere.
- **⚠ What is NOT superseded:** the §1.3 off-by-two correction. Both reported EMC types retain
  NR4A3 from its own first coding exon, so AF-1, the C4 zinc finger and the LBD are present under
  either type, and `fusion_cofold.py`'s model remains the exon-compatible one.
