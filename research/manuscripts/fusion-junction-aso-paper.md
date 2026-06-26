# A fusion-selective antisense oligonucleotide against the EWSR1::NR4A3 breakpoint junction: RNA-level fusion-exclusivity that the NR4A3 degrader cannot reach

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
> [`../modalities/junction-aso-offtarget-bp200-8-gapres.json`](../modalities/junction-aso-offtarget-bp200-8-gapres.json)
> (2 of 5 gapmers predicted clean — zero true RNase-H cleavage risk), corroborated by an uncapped
> full-transcriptome screen on the same favorable breakpoint
> [`../modalities/aso-insilico-evaluation-bp200-8.json`](../modalities/aso-insilico-evaluation-bp200-8.json)
> (4 of 5 gapmers with zero ≤1-mismatch off-targets; 5 of 5 with zero exact — vs 0 of 5 clean at the
> canonical junction). Together these show feasibility is
> **breakpoint-conditional but breakpoint-selectable**: specificity and chemistry at the *canonical* modelled
> junction are poor, but that is a property of that junction position — a clear majority of modelled
> breakpoints yield clean, in-band, fusion-specific designs — not of the modality. **The fusion-selectivity rationale in one line:** the breakpoint mRNA seam is
> present *only* in the chimera, so an RNase-H gapmer (or siRNA) targeting the junction silences
> EWSR1::NR4A3 while sparing wild-type *EWSR1* and wild-type *NR4A3* — true fusion-exclusivity, which an
> LBD-binding degrader (identical domain in fusion and wild-type) cannot achieve. Every clinical/quantitative
> claim is cited, computed from committed repo output, or flagged as a design hypothesis. Nothing here is a
> validated drug or clinical evidence.

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
sweeping **390 modelled breakpoints**, the canonical position is indeed unfavorable, but **243 (62%) are
favorable** — yielding balanced (~50% GC), fusion-specific in-band gapmer *and* siRNA designs (e.g. a 5-6-5
gapmer `GCTATACGGCTGTGTA` at 50.0% GC with an in-band siRNA at 52.6% GC). So feasibility is
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
EMC-program roadmap]. A therapy that neutralises the fusion transcript should therefore reach essentially
every tumour cell, with no large mutational landscape offering obvious escape.

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

## 2. The approach: junction-spanning gapmer or siRNA

Two transcript-level mechanisms can exploit the junction; both require the active sequence to **straddle**
the breakpoint so that fusion-exclusivity is enforced by base-pairing.

**(a) RNase-H1 gapmer (lead).** A gapmer is a short oligo with a central DNA "gap" flanked by modified
"wings" (LNA — locked nucleic acid — or cEt — constrained ethyl). The wings raise affinity and nuclease
resistance; the DNA gap, once hybridised to the target, recruits endogenous RNase-H1 to cleave the RNA
strand [Crooke et al. 2021]. For fusion-exclusivity the central DNA gap must span the junction, because
RNase-H1 cleaves within the DNA:RNA duplex of the gap — so the cleaved bond sits across the tumour-specific
seam, and a parent transcript (matching only one wing-plus-partial-gap) does not form the contiguous duplex
needed for catalysis. The committed designs (§3) use a 16-mer **5-6-5** LNA/DNA/LNA architecture; the
design script's docstring also references the common **5-10-5** gapmer layout as the standard template
[`junction_aso.py`].

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

> **Integrity flag (breakpoint is modelled).** The committed designs use an *assumed* canonical breakpoint
> (the JSON marks `_breakpoint_model.assumption = true`). They are correct as a worked example of the
> method, but for any clinical design the script must be re-run on a patient's **sequenced** fusion
> transcript (§3b). The five sequences are design hypotheses, not a drug.

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
- **Target site is moderately accessible** (mean unpaired probability **0.34–0.42** across the five) — i.e.
  potency is not obviously gated by mRNA structure at this junction; specificity, not accessibility, is the
  canonical junction's problem.
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
[`novel-modalities.md`](./novel-modalities.md) §3.3), some of which are likely more favorable. The
conclusion is therefore that ASO/siRNA feasibility is **breakpoint-conditional**: designs must be re-run on
the patient's *sequenced* breakpoint, and junction sequence-favorability (GC content, complexity,
off-target load) becomes a **patient/breakpoint selection criterion**. This tempers but does not overturn
the route's standing — the *mechanism* (knockdown of an addicted fusion transcript) remains the most
de-risked of the fusion-exclusive routes, and the per-breakpoint scan below (§3a-ter) shows that a clear
majority of modelled breakpoints *do* yield clean, in-band designs — so the canonical junction's poor
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
- A **well-balanced favorable example** (EWSR1 keep 200 / NR4A3 from 8) has junction GC ±10 nt = **50.0%**
  and yields a fusion-specific 5-6-5 gapmer `5′-GCTATACGGCTGTGTA-3′` (target mRNA `TACACAGCCGTATAGC`,
  **GC 50.0%**, specificity margin 6, no G-quadruplex motif) *together with* an in-band siRNA guide
  (**GC 52.6%**) — i.e. a clean, balanced design on both routes. (The scan's single lowest-GC position,
  EWSR1 keep 204 / NR4A3 from 16, is even lower at 35% junction GC but is GC-skewed; the 200/8 example is
  reported here because it sits squarely in band on both modalities.)

**Honest caveats on the scan (stated as plainly as the result):**

1. **These are MODELLED breakpoint positions** — a codon-space sensitivity sweep, not exon-exact clinical
   breakpoints. The 62% is a property of the swept grid, **not** a claim about how often real patients carry
   a favorable breakpoint; the companion exon work (EWSR1 exons 7/9/10/11/12/13 → predominantly NR4A3 exon 3;
   [`novel-modalities.md`](./novel-modalities.md) §3.3) is bracketed in codon space here, not mapped exon-exact.
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
BLAST off-target screen on that specific design. This strengthens the route's standing as the most
mechanistically de-risked of the fusion-exclusive options, with breakpoint-favorability now demonstrated to
be selectable rather than a roadblock.

### 3a-quater. Two off-target screens on a favorable breakpoint — gap-resolved BLAST + uncapped full-transcriptome
We ran the full §3a-bis(i) off-target screen *directly on the favorable 200/8 breakpoint* (junction GC
50 %), then **resolved each near-match to the gap-mismatch level** — because RNase-H needs the central DNA
gap (the 6 nt the gapmer cleaves through) fully base-paired: a near-match whose mismatch falls *inside* the
gap **cannot be cleaved** and is not a real liability
([`junction-aso-offtarget-bp200-8-gapres.json`](../modalities/junction-aso-offtarget-bp200-8-gapres.json)).
This is decisive, and positive:
- **GC-triage alone is necessary but not sufficient**, and the coarse "gap-spanning" count *over-states*
  risk. Every near-match at this breakpoint is a weak **14/16** (2-mismatch) hit to a real gene
  (CSMD2, ADAMTSL2, DDR1, SLC66A1…), versus the canonical junction's stronger 15/16 hits.
- **Once gap-mismatch position is resolved, 2 of the 5 gapmers are predicted genuinely clean — zero true
  cleavage risks.** The gapmer (antisense) `5′-GGGCTATACGGCTGTG-3′` (62.5 % GC; target mRNA
  `CACAGCCGTATAGCCC`) has 21 off-target near-matches but **all 21 are gap-disrupted** (the mismatch lands in
  the DNA gap) → 0 cleavable; `5′-AGGGCTATACGGCTGT-3′` (56.2 % GC; target mRNA `ACAGCCGTATAGCCCT`) has a
  **single** off-target near-match, also gap-disrupted → 0 cleavable. The other three retain 15, 27 and 29
  true cleavage risks.
- So **per-oligo selection is as important as breakpoint selection**, and the deciding filter is the
  gap-mismatch-resolved BLAST screen, not raw GC or raw near-match count.
- **An orthogonal, uncapped full-transcriptome screen confirms it — and more cleanly.** We re-ran the §3a-bis(iii)
  uncapped evaluation (full RefSeq, 186,185 transcripts; seed-and-extend) *on this same 200/8 favorable
  breakpoint* ([`aso-insilico-evaluation-bp200-8.json`](../modalities/aso-insilico-evaluation-bp200-8.json)).
  The contrast with the canonical junction is stark: **all 5 gapmers have 0 exact off-targets and 4 of 5 have
  0 near-perfect (≤1-mismatch) off-targets** transcriptome-wide (the fifth has just 1), where the *canonical*
  designs had 0 of 5 clean and 8–95 ≤1-mismatch hits. The two predicted-clean designs from the BLAST screen
  (`GGGCTATACGGCTGTG`, `AGGGCTATACGGCTGT`) are among the four with zero ≤1-mismatch off-targets here, so the
  screens agree. The siRNA-seed load also collapses at this breakpoint (the junction-straddling seed of
  `GCTATACGGCTGTGTA` matches **3,366** transcriptome sites, vs ~119,000 for the GC-rich canonical seed). The
  one honest reconciliation: the two screens use different stringency — the uncapped screen counts ≤1-mismatch
  (≥15/16) full-length hits and calls 4 of 5 clean, while the wider BLAST screen counts ≥14/16 (≤2-mismatch)
  near-matches and, after gap-resolution, calls 2 of 5 clean of *true* cleavage risk. Both agree the favorable
  breakpoint yields predicted-clean gapmers; the exact count (2 vs 4) is set by how many mismatches one allows
  an off-target before counting it.

**Reading.** At a favorable breakpoint, the full workflow — breakpoint triage → per-oligo BLAST →
gap-mismatch resolution, now corroborated by an independent uncapped full-transcriptome screen — **does yield
predicted-clean gapmers** (2 of 5 free of true ≤2-mismatch cleavage risk; 4 of 5 free of any ≤1-mismatch
off-target), a path the GC-rich canonical junction could not offer. Specificity is therefore **achievable**,
not merely improvable, at the right breakpoint. Honest bounds remain: this is *predicted* (a 14/16 hit with a
gap mismatch is assumed non-cleaving per standard RNase-H behaviour, to be confirmed experimentally), the
breakpoint is *modelled* not patient-sequenced, and delivery (§3c) is the separate, still-unsolved gate.
The route stands as the most mechanistically de-risked fusion-exclusive option, now with *demonstrated
in-silico specificity feasibility* — under both a capped-BLAST and an uncapped full-transcriptome screen — at
a selectable breakpoint.

### 3b. What is specifiable now, without any GPU

All of the following are CPU-only and need no new GPU/compute run; they are specified, not executed, in
this draft:

1. **Expanded tiling.** Re-run the existing tiler over a wider window and multiple oligo lengths (e.g.
   14–20-mers) and both 5-6-5 and 5-10-5 architectures, to enumerate the full junction-spanning design
   space rather than the top-5 snapshot, and to find any lower-GC register that still straddles the seam.
2. **Genome-wide off-target complementarity screen (CPU) — DONE for the modelled breakpoint (§3a-bis i).**
   The current design-time check only confirms an oligo is not a *perfect* complement of the two parent
   CDSs; a real specificity claim requires a transcriptome-wide near-match search with gap-region weighting
   (RNase-H tolerates wing mismatches more than gap mismatches). **This has now been run** (blastn-short vs
   RefSeq RNA) on the modelled-breakpoint (canonical) designs and returned a poor verdict (0 of 5 free of
   gap-spanning near-matches) — but that was the *unfavorable canonical* junction. With the per-breakpoint
   scan now complete (§3a-ter), the decisive remaining step is to **run this BLAST off-target screen on a
   chosen favorable breakpoint** (e.g. the in-band EWSR1 200 / NR4A3 8 example), where the input design is
   already ~50% GC and in-band — the screen is no longer being asked to rescue an intrinsically GC-rich,
   low-complexity seam. (The uncapped re-screen the over-call called for is **now done** for the canonical
   designs via a full local RefSeq scan — §3a-bis iii,
   [`aso-insilico-evaluation.json`](../modalities/aso-insilico-evaluation.json) — giving true ≤1-mismatch
   counts of 8–95 in place of the capped 50.)

   **Per-breakpoint feasibility scan — DONE (§3a-ter).** The sensitivity sweep over 390 modelled breakpoints
   has been run and committed ([`junction-breakpoint-scan.json`](../modalities/junction-breakpoint-scan.json)):
   243/390 (62%) are favorable, the canonical position is not, and favorable in-band designs exist. This is
   the step that turned "breakpoint-conditional" into "breakpoint-selectable"; the only remaining work above
   it is the BLAST screen on a chosen favorable breakpoint.
3. **siRNA alternative (computable) — DONE for the modelled breakpoint (§3a-bis ii).** Junction-spanning
   19-mer siRNA guides have now been generated (asymmetry/end-stability/run filters); at this breakpoint 0
   of 5 pass (min GC 73.7%), so the GC-tolerant route does not rescue this junction. Seed off-target
   counting against the transcriptome remains specifiable for any breakpoint that yields in-window-GC guides.
4. **Breakpoint heterogeneity → a per-patient panel.** Because EMC breakpoints vary by exon usage (the
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
Options below are **hypotheses, explicitly flagged**, not validated approaches:

- **Receptor-targeted antibody–oligonucleotide conjugate (AOC).** Couple the gapmer/siRNA to an antibody
  against a surface antigen enriched on EMC cells. **B7-H3 (CD276)** is one candidate worth evaluating as
  an EMC surface marker — *flagged as a hypothesis to verify; B7-H3 expression in EMC specifically is
  [citation to verify].* AOC platforms exist in other indications but none is established for EMC.
- **Receptor-/ligand-targeted nanoparticle (LNP or polymer).** Encapsulate the oligo and decorate with a
  ligand for an EMC-enriched receptor. Again, the specific EMC-enriched receptor is the unsolved input
  [citation to verify].
- **Local/intratumoural administration** for accessible lesions, sidestepping systemic targeting — a
  narrower but more tractable first-in-human setting (hypothesis).

No delivery claim is made; this section exists to mark delivery as the dominant risk, not to assert a
solution.

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

This is the experiment that converts five sequences and a mechanism into evidence. It needs no new molecule
beyond synthesising the listed oligos and no new biology beyond the published EMC models.

---

## 5. Selectivity and safety

- **Fusion-exclusive by sequence.** The active oligo spans the breakpoint; neither parent mRNA presents the
  contiguous junction duplex required for RNase-H (gapmer) or RISC (siRNA) cleavage. Selectivity is
  enforced by base-pairing, not by protein conformation.
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
- **Poor predicted specificity at the modelled breakpoint.** The committed off-target screen (§3a-bis i)
  found **0 of 5** gapmers free of gap-spanning (RNase-H-cleavable) near-matches across the transcriptome,
  and the GC-tolerant siRNA route did not rescue it (0 of 5 guides pass; min GC 73.7%, §3a-bis ii). This
  is a real, committed result. The BLAST 50-near-match figure is over-called (HITLIST capped at 50,
  low-complexity filter off, on a low-complexity GC-rich window), so it is a floor in character; the
  **uncapped** full-transcriptome re-screen (§3a-bis iii) replaces that floor with true counts — all five
  gapmers have 0 exact matches and 8–95 ≤1-mismatch off-targets, with `n_candidates_zero_offtarget = 0` — so
  the qualitative verdict (this canonical junction is specificity-poor) is robust under both the capped and
  the uncapped screen. That same evaluation also flags a large siRNA-seed off-target load (~21k–119k seed
  sites) for the GC-rich seam.
- **Breakpoint-conditional — a tractable selection step, not a roadblock.** Feasibility (chemistry GC,
  siRNA GC, predicted specificity) is a property of the *junction sequence*, not of the modality, and the
  **canonical** modelled junction is genuinely unfavorable. But the per-breakpoint scan (§3a-ter) shows
  **243 of 390 modelled breakpoints (62%) are favorable** — yielding balanced (~50% GC), fusion-specific
  in-band designs on both routes — so junction-favorability is a *selectable* patient/breakpoint criterion,
  not a fatal flaw. Honest bounds on this reassurance: the swept breakpoints are **modelled (codon-space),
  not exon-exact**, so 62% describes the grid, not real-patient breakpoint frequencies; "favorable" is a
  GC/complexity/parent-substring **triage, not the full BLAST off-target screen** (which must be re-run on a
  chosen favorable design); and every clinical design must still be re-derived from the patient's
  *sequenced* fusion transcript (the committed designs use a *modelled* breakpoint).
- **Delivery unsolved.** No validated tumour-delivery route for EMC exists; §3c lists hypotheses only. This
  is the dominant risk for the whole modality.
- **Knockdown, not knockout.** ASO/siRNA reduce transcript; they do not eliminate the gene or guarantee
  durable, complete loss of fusion protein. Depth and duration of knockdown are empirical.
- **Predicted specificity ≠ validated specificity.** The transcriptome-wide near-match screen has now been
  **run** for the modelled breakpoint (§3a-bis i) and returned a poor result, but it remains *in-silico*
  predicted specificity — and over-called by the 50-cap / no-low-complexity-filter settings. Only the §4
  wet-lab experiment can confirm parental and off-target sparing in cells.
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

## References

Verified reference pool (appear verified in the repo):

- **Sjögren H, et al.** *EWSR1/NR4A3 fusion in extraskeletal myxoid chondrosarcoma.* (EMC defining fusion.)
- **Panagopoulos I, et al.** *Fusion variants and partners in EMC* (incl. TAF15, TCF12, TFG, FUS).
- **Crooke ST, et al.** *Antisense technology: an overview and prospectus.* **Nat Rev Drug Discov** 2021.
  doi:10.1038/s41573-021-00162-z. (Antisense / gapmer / RNase-H1 mechanism overview.)
- **Bangerter, et al.** USZ-EMC patient-derived EMC model (2023).
- **Iwata S, et al.** NCC-EMC patient-derived EMC cell lines.
- **Mullican SE, et al.** *Abrogation of Nr4a3 and Nr4a1 leads to acute myeloid leukemia.* **Nat Med** 2007.
  (Wild-type NR4A1/NR4A3 loss → AML — the tumour-suppressor liability the junction ASO avoids.)
- **Safe S, Karki K.** *The paradoxical roles of orphan nuclear receptor 4A (NR4A) in cancer.* **Mol Cancer
  Res** 2021. (NR4A3 tumour-suppressor roles in HCC/breast/lymphoma.)
- **Le Guilloux V, Schmidtke P, Tufféry P.** *Fpocket.* **BMC Bioinformatics** 2009. (Referenced for the
  companion structural/degrader work; not used in this RNA-level analysis.)
- **Varadi M, et al.** *AlphaFold Protein Structure Database.* **Nucleic Acids Res** 2022.
  doi:10.1093/nar/gkab1061. (Referenced for the companion structural work; not used here.)

To verify (do **not** treat as established until sourced):

- B7-H3 (CD276) surface expression in EMC specifically — **[citation to verify]**.
- EMC-enriched surface receptor(s) suitable for AOC / targeted-nanoparticle delivery — **[citation to verify]**.
- Specific non-EWSR1/FET recurrent-fusion cancers as platform extensions — **[citation to verify]** per indication.

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

No GPU computation was performed for this draft.
